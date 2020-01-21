from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from auto_mechop.util import cd
import logging
import time
import math

from auto_mechop.util import match_filename_to_student


logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.ERROR)


class GoogleDriveService:
    def __init__(self):
        self.DRIVE = self.get_authenticated_service()

    @staticmethod
    def get_authenticated_service():
        """
        Builds and returns an authenticated Google API service.
        """
        SCOPES = 'https://www.googleapis.com/auth/drive'
        store = file.Storage('storage.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            flags = tools.argparser.parse_args(args=[])
            creds = tools.run_flow(flow, store, flags=flags)
        DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()), cache_discovery=False)
        time.sleep(1)
        return DRIVE

    def upload_assignment_by_section(self, graders, sections, section_name, assignment_name):
        section = sections[section_name]

        # get or create the folder structure for the graders
        for grader_id, grader in graders.items():
            if assignment_name not in grader.assignment_folder_ids:
                grader.assignment_folder_ids[assignment_name] = dict()
                assignment_folder = self.create_folder(grader.fileid, assignment_name)
                grader.assignment_folder_ids[assignment_name]['root'] = assignment_folder
                grader.assignment_folder_ids[assignment_name]['assigned'] = self.create_folder(assignment_folder,
                                                                                               'Assigned')
                grader.assignment_folder_ids[assignment_name]['graded'] = self.create_folder(assignment_folder,
                                                                                             'Graded')

        # get assignments to upload from the section
        assignments_to_upload = set()
        for student_id, student in section.items():
            if assignment_name in student.assignments:
                assignments_to_upload.add(student.assignments[assignment_name])

        # iterate over assignments and upload
        # best to batch permissions changes and upload at the same time
        batch = self.DRIVE.new_batch_http_request(callback=self.callback)

        logger.info('')
        for assignment in assignments_to_upload:

            with cd('../temp/' + assignment_name + '_' + section_name):
                grader = graders[assignment.grader_id]
                file_id = self.create_file(assignment.filename,
                                           grader.assignment_folder_ids[assignment_name]['assigned'])
                assignment.file_id = file_id
                permission_level = 'writer'
                logger.debug('Applied role {} to student {} for file {}'.format(permission_level,
                                                                                section[assignment.student_id].usc_id,
                                                                                assignment.filename))
        logger.info('')

        # apply permissions (need to give GDrive a sec to sort itself out, create_file doesn't block correctly
        logger.info('Applying permissions')
        time.sleep(2)
        batch.execute()


    def release_assignment_by_section(self, graders, section, assignment_name):
        # get all assignments uploaded to the graded folders for this assignment
        uploaded_assignments = set()
        for grader_id, grader in graders.items():
            graded_folder = grader.assignment_folder_ids[assignment_name]['graded']
            files = self.list_files_in_folder(graded_folder)
            for filedata in files:
                uploaded_assignments.add((filedata['name'], filedata['id']))

        # match with students in this section only
        uploaded_assignments_section_only = set()
        for assignment in uploaded_assignments:
            student = None
            try:
                student = match_filename_to_student(assignment[0], section)
            except AttributeError:
                pass
            if student is not None:
                assignment_with_student = (assignment[0], assignment[1], student)
                uploaded_assignments_section_only.add(assignment_with_student)

        # update permissions to allow students in this section to view their files
        batch = self.DRIVE.new_batch_http_request(callback=self.callback)
        counter = 0
        batch_groups = list()
        for assignment_name, assignment_fileid, student in uploaded_assignments_section_only:
            if counter > 10:
                batch_groups.append(batch)
                counter = 0
                batch = self.DRIVE.new_batch_http_request(callback=self.callback)

            permission_level = 'commenter'
            self.add_single_permission_to_batch(batch, assignment_fileid, student.email, permission_level)
            logger.debug('Applying role {} to student {} for file {}'.format(permission_level,
                                                                            student.name,
                                                                            assignment_name))
            counter += 1
        batch_groups.append(batch)



        # apply permissions (need to give GDrive a sec to sort itself out, create_file doesn't block correctly
        logger.info('Applying permissions to Google Drive')
        time.sleep(2)
        for batch in batch_groups:
            batch.execute()
            time.sleep(2)
        logger.info('')
        logger.info('Finished releasing assignment to students')

    @staticmethod
    def callback(request_id, response, exception):
        if exception:
            logger.error('Google Drive upload error')
            logger.error(exception)
        else:
            logger.debug("Permission Id: %s" % response.get('id'))

    def list_files_in_folder(self, folder_id):
        query = "'{}' in parents".format(folder_id)
        files = self.DRIVE.files().list(q=query,
            fields='files(id, name)').execute().get('files', [])
        return files

    def create_folder(self, parent_id, folder_name):
        """
        Creates a folder with specified name and parent.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file_data = self.DRIVE.files().create(body=file_metadata,
                                            fields='id').execute()
        folder_id = file_data.get('id')
        return folder_id

    def create_file(self, filename, parent_id, mimeType=None):
        """
        Creates a file on Google drive. FILE is a tuple of (filename, mimetype).
        Example: ('3206948547_7_M_E9_Trojan_Tommy.pdf', 'application/pdf')
        """
        metadata = {'name': filename,
                    'parents': [parent_id]}
        if mimeType:
            metadata['mimeType'] = mimeType

        file_data = self.DRIVE.files().create(body=metadata, media_body=filename).execute()
        if file_data:
            logger.info('Uploaded "%s" (%s)' % (filename, file_data['mimeType']))
        return file_data.get('id')

    def add_single_permission_to_batch(self, batch, file_id, email, role):
        domain_permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        batch.add(self.DRIVE.permissions().create(
            fileId=file_id,
            sendNotificationEmail=False,
            body=domain_permission,
            fields='id',
        ))

    def delete_file(self, file_id):
        body = {'trashed': True}
        updated_file = self.DRIVE.files().update(fileId=file_id, body=body).execute()
        return updated_file

if __name__ == "__main__":
    drive = GoogleDriveService()
    print(drive.list_files_in_folder('root'))

