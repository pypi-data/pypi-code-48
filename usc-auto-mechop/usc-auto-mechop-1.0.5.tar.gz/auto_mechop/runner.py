import pickle
import zipfile
import os
import shutil
import re

from auto_mechop.submit import AssignmentDistributionCoordinator
from auto_mechop.google_drive import GoogleDriveService
from auto_mechop.util import cd, match_filename_to_student
from auto_mechop.semester import Semester

import logging

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self):
        logger.debug('Runner instantiated')
        self.semester = None
        self.semester_name = None
        self.assignment_name = None
        self.section_name = None

    def run_setup_flow(self):
        # if we already have a .pkl file, use that
        try:
            self.semester = self.load()
            # update everything as normal
            self.semester.each_run_update('../config/auto_mechop.xlsx')
            self.save()


        # otherwise create everything from scratch
        except FileNotFoundError:
            self.semester = Semester()
            self.semester.initial_setup('../config/auto_mechop.xlsx')
            self.semester_name = self.semester.name
            logger.info('Completed initial setup')
            self.save()

    def run_submit_flow(self, args):

        # load semester
        self.assignment_name = args.assignment_name
        self.section_name = args.section_name
        self.semester = self.load()
        self.semester_name = self.semester.name

        logger.info('Submitting assignment {} for section {}\n'.format(self.assignment_name,
                                                                       self.section_name))
        # download, if user requests

        # unpack folder
        folder_name = self.assignment_name + '_' + self.section_name + '.zip'
        with cd('../temp'):
            unpacked_folder = unpack_folder(folder_name)

            # run distribution of assignments in the unpacked folder
            distributor = AssignmentDistributionCoordinator(unpacked_folder)
            distributor.assignment_name = self.assignment_name
            distributor.assign(self.semester.graders,
                               self.semester.sections[self.section_name],
                               self.semester.preselections,
                               self.semester.exclusions)

        # attempt an upload
        uploader = GoogleDriveService()
        uploader.upload_assignment_by_section(self.semester.graders,
                                              self.semester.sections,
                                              self.section_name,
                                              self.assignment_name)
        logger.info('Upload to Google Drive complete\n')
        self.save()
        logger.info('Submission complete')

    def run_clear_flow(self, args):
        self.assignment_name = args.assignment_name
        self.semester = self.load()
        self.semester_name = self.semester.name

        logger.info("Clearing assignment {}".format(self.assignment_name))
        logger.info("Removing files from Google Drive")
        for grader_id, grader in self.semester.graders.items():

            for assignment in grader.assignments_graded[self.assignment_name]:
                print(assignment.filename)
                import pdb;
                pdb.set_trace()
                drive_service = GoogleDriveService()
                drive_service.delete_file(assignment.file_id)

    def run_release_flow(self, args):
        self.semester_name = 'test_semester'
        self.assignment_name = args.assignment_name
        self.section_name = args.section_name
        self.semester = self.load()

        logger.info('Releasing assignment {} for section {}\n'.format(self.assignment_name,
                                                                      self.section_name))
        uploader = GoogleDriveService()
        uploader.release_assignment_by_section(self.semester.graders,
                                               self.semester.sections[self.section_name],
                                               self.assignment_name)

    def run_report_flow(self, args):
        self.semester_name = 'test_semester'
        self.assignment_name = args.assignment_name
        self.semester = self.load()

        logger.info('Running report for assignment {}\n'.format(self.assignment_name))

        logger.info('STUDENTS WITHOUT SUBMISSIONS:\n')
        for section_name, section in self.semester.sections.items():
            counter = 0
            logger.info('Section: ' + section_name)
            for student_id, student in section.items():
                if self.assignment_name not in student.assignments:
                    logger.info(student.name)
                    counter += 1
            logger.info('Total: {} students have not been submitted for {}'.format(counter, section_name))
            logger.info('')

        logger.info('GRADERS THAT HAVE NOT UPLOADED GRADED ASSIGNMENTS:')
        uploader = GoogleDriveService()
        for grader_id, grader in self.semester.graders.items():
            assigned_folder_id = grader.assignment_folder_ids[self.assignment_name]['assigned']
            graded_folder_id = grader.assignment_folder_ids[self.assignment_name]['graded']

            assigned_files = uploader.list_files_in_folder(assigned_folder_id)
            graded_files = uploader.list_files_in_folder(graded_folder_id)

            assigned_students = set()
            graded_students = set()

            for file in assigned_files:
                filename = file['name']
                try:
                    usc_id_from_filename = int(re.search("\d{10}", filename).group(0))
                    assigned_students.add(usc_id_from_filename)
                except AttributeError:
                    print('Unrecognized filename {} from grader {}'.format(filename, grader.name))

            for file in graded_files:
                filename = file['name']
                try:
                    usc_id_from_filename = int(re.search("\d{10}", filename).group(0))
                    graded_students.add(usc_id_from_filename)
                except AttributeError:
                    print('Unrecognized filename {} from grader {}'.format(filename, grader.name))
            ungraded_students = assigned_students.difference(graded_students)
            if len(ungraded_students) > 0:
                logger.info(grader.name + ' ({} assignments not yet uploaded):'.format(len(ungraded_students)))
                for student_id in ungraded_students:
                    student = self.semester.match_usc_id_to_student(student_id)
                    logger.info('\t' + student.name)

    def save(self):
        with open('auto_mechop.pkl', 'wb') as handle:
            pickle.dump(self.semester, handle, pickle.HIGHEST_PROTOCOL)
            logger.debug('Saved file to disk')

    def load(self):
        with open('auto_mechop.pkl', 'rb') as handle:
            semester = pickle.load(handle)
            logger.debug('Loaded file from disk')
        return semester


def unpack_folder(zip_filename):
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        folder_name = os.path.splitext(zip_filename)[0]
        # clear any preexisting folder with that name
        try:
            shutil.rmtree(folder_name)
        except IOError:
            pass
        zip_ref.extractall(folder_name)

    return folder_name
