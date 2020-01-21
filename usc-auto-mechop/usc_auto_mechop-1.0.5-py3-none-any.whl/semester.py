import xlrd
import pandas as pd

from auto_mechop.google_drive import GoogleDriveService

import logging
logger = logging.getLogger(__name__)


# semester is the top-level object that contains all the child data
class Semester:
    def __init__(self):
        # students and graders are dicts with [USC ID]:[person]
        self.graders = dict()
        self.assignments = dict()
        self.exclusions = list()
        self.sections = dict()
        self.name = None
        self.preselections = list()
        # fileid for the top-level GDrive folder in which the semester data is stored
        self.fileid = None
        self.config_dict = None


    def initial_setup(self, filename):
        processor = ExcelConfigFileProcessor(filename)
        self.graders, self.exclusions, self.sections, self.preselections, self.config_dict = processor.\
            process_entire_file()
        self.name = self.config_dict['semester_name']

        self.create_top_level_drive_folders()

    def each_run_update(self, filename):
        processor = ExcelConfigFileProcessor(filename)
        # overwrite preselections and exclusions with whatever we pull from the file
        # TODO fix so that students aren't fully overwritten
        updated_graders, self.exclusions, self.sections, self.preselections, self.config_dict = processor.\
            process_entire_file()

        new_graders = list()
        for grader_id, _ in self.graders.items():
            self.graders[grader_id].assignments_required = 0

        for grader_id, grader in updated_graders.items():
            # for any current graders, only update the number of assignments
            if grader_id in self.graders.keys():
                updated_num_assignments = updated_graders[grader.usc_id].assignments_required
                self.graders[grader_id].assignments_required = updated_num_assignments
            # for any new graders, add them to the graders object and create their Google Drive folder
            else:
                new_graders.append(grader)
                self.graders[grader_id] = grader

        if new_graders:
            logger.info('Adding new graders to Google Drive file structure')
            uploader = GoogleDriveService()
            batch = uploader.DRIVE.new_batch_http_request(callback=uploader.callback)
            for grader in new_graders:
                grader.fileid = uploader.create_folder(self.fileid, grader.name + '--AME 341 grading')
                permission_level = 'writer'
                uploader.add_single_permission_to_batch(batch, grader.fileid, grader.email, permission_level)
            batch.execute()
            logger.info('Finished adding new graders')


    def create_top_level_drive_folders(self):
        logger.info('Creating Google Drive file structure')
        uploader = GoogleDriveService()
        # root folder
        self.fileid = uploader.create_folder('root', 'AME 341 grading: ' + self.name)
        # grader folders
        batch = uploader.DRIVE.new_batch_http_request(callback=uploader.callback)
        for _, grader in self.graders.items():
            grader.fileid = uploader.create_folder(self.fileid, grader.name + '--AME 341 grading')
            permission_level = 'writer'
            uploader.add_single_permission_to_batch(batch, grader.fileid, grader.email, permission_level)
        batch.execute()

    def match_usc_id_to_student(self, usc_id):
        for _, section in self.sections.items():
            if usc_id in section:
                return section[usc_id]

        return None


class Person:
    def __init__(self, usc_id, name, email):
        self.usc_id = usc_id
        self.name = name
        self.email = email


class Student(Person):
    def __init__(self, usc_id, name, email, section_name):
        Person.__init__(self, usc_id, name, email)
        self.section_name = section_name
        self.assignments = dict()


class Grader(Person):
    def __init__(self, usc_id, name, email, assignments_required):
        Person.__init__(self, usc_id, name, email)
        self.assignments_required = assignments_required
        self.assignments_graded = dict()
        self.fileid = None
        self.assignment_folder_ids = dict()


class ExcelConfigFileProcessor:
    def __init__(self, filename):
        self.filename = filename

    # main utility method for building and returning the parts of the semester object we want to populate
    def process_entire_file(self):
        logger.info('Processing semester information file located at {}'.format(self.filename))
        graders_dict = self._read_grader_sheet()
        exclusions_list = self._read_exclusion_sheet()
        sections_dict = self._read_student_sheets()
        preselections_list = self._read_preselections_sheet()
        config_dict = self._read_config_sheet()

        return graders_dict, exclusions_list, sections_dict, preselections_list, config_dict

    def process_exclusions_and_preselections(self):
        logger.debug('Updating exclusions and preselections')
        exclusions_list = self._read_exclusion_sheet()
        preselections_list = self._read_preselections_sheet()
        graders_dict = self._read_grader_sheet()
        return exclusions_list, preselections_list, graders_dict


    def _read_grader_sheet(self):
        logger.info("Updating grader information")
        graders_dict = dict()
        df = pd.read_excel(self.filename, sheet_name='graders')
        for row in df.itertuples(index=False):
            grader = Grader(row.usc_id,
                            row.name,
                            row.email,
                            row.required_assignments)
            graders_dict[row.usc_id] = grader
            logger.debug('Added {} as a grader'.format(grader.name))
        return graders_dict


    def _read_student_sheets(self):
        logger.info('Updating student information')
        xls = xlrd.open_workbook(self.filename, on_demand=True)
        sheets = xls.sheet_names()
        sections_dict = dict()
        for sheet in sheets:
            if sheet.split('_')[0] == 'section':
                df = pd.read_excel(self.filename, sheet_name=sheet)
                section_name = sheet.split('_')[1]
                students_dict = dict()
                for row in df.itertuples(index=False):
                    student = Student(row.usc_id,
                                      row.name,
                                      row.email,
                                      section_name)
                    students_dict[row.usc_id] = student
                    logger.debug('Added {} as a student in {} section'.format(student.name, section_name))
                sections_dict[section_name] = students_dict

        return sections_dict

    def _read_exclusion_sheet(self):
        logger.info("Updating exclusion information")
        exclusions_list = list()
        df = pd.read_excel(self.filename, sheet_name='exclusions')
        for row in df.itertuples(index=False):
            exclusions_list.append((row[0], row[1]))
        return exclusions_list

    def _read_preselections_sheet(self):
        logger.info("Updating preselection information")
        preselection_list = list()
        df = pd.read_excel(self.filename, sheet_name='preselections')
        for row in df.itertuples(index=False):
            preselection_list.append((row[0], row[1], row[2]))
        return preselection_list

    def _read_config_sheet(self):
        logger.info('Reading config information')
        config_dict = dict()
        df = pd.read_excel(self.filename, sheet_name='config')
        for row in df.itertuples(index=False):
            config_dict[row[0]] = row[1]
        return config_dict



