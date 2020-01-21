import zipfile
import os
import re
import shutil
import random
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import math

import logging
logger = logging.getLogger(__name__)

from auto_mechop.util import cd, match_filename_to_student

class Assignment:

    def __init__(self, filename, student_id):
        self.filename = filename
        self.student_id = student_id
        self.grader_id = None
        self.file_id = None


class AssignmentDistributionCoordinator:
    def __init__(self, assignment_folder_path):
        self.assignment_folder_path = assignment_folder_path
        self.assignment_name = None
        self.number_of_submitted_assignments = 0
        self.number_of_total_grading_slots = 0
        self.proportional_assignments_to_grade = dict()
        self.number_of_assignments_already_given = dict()
        self.current_preselections = list()

    def assign(self, graders, section, preselections, exclusions):
        with cd('./' + self.assignment_folder_path):

            logger.info('Assigning to graders:')

            # set up grader metadata
            for grader_id, grader in graders.items():
                self.number_of_total_grading_slots += grader.assignments_required
                try:
                    grader.assignments_graded[self.assignment_name]
                except KeyError:
                    grader.assignments_graded[self.assignment_name] = list()
            self.number_of_assignments_already_given = dict.fromkeys(graders.keys(), 0)

            # step 1: grab all the files that have been submitted in ./temp
            assignment_filenames = os.listdir()

            # step 2: match filenames to students and build our assignment objects
            submitted_assignments = set()
            submitted_student_usc_id = set()
            assigned_assignments = set()
            for filename in assignment_filenames:
                student = None
                try:
                    student = match_filename_to_student(filename, section)
                except AttributeError:
                    logger.info('Unable to match file {} to any student, could not find a 10-digit USC ID in the filename.'.format(filename))

                # if a student is found, add them to the submitted pool
                # otherwise, just skip them entirely
                if student is not None:
                    new_assignment = Assignment(filename, student.usc_id)
                    student.assignments[self.assignment_name] = new_assignment
                    submitted_student_usc_id.add(student.usc_id)
                    submitted_assignments.add(new_assignment)

            self.number_of_submitted_assignments = len(submitted_assignments)

            for grader_id, grader in graders.items():
                self.proportional_assignments_to_grade[grader_id] = \
                    math.ceil(grader.assignments_required / self.number_of_total_grading_slots
                              * self.number_of_submitted_assignments)

            # step 3: satisfy all preselections
            for preselected_grader, preselected_student, preselected_assignment in preselections:
                if preselected_assignment == self.assignment_name:
                    self.current_preselections.append(preselected_grader)
                if preselected_assignment == self.assignment_name and preselected_student in submitted_student_usc_id:
                    selected_assignment = section[preselected_student].assignments[self.assignment_name]
                    graders[preselected_grader].assignments_graded[self.assignment_name]\
                        .append(selected_assignment)
                    self.number_of_assignments_already_given[preselected_grader] += 1
                    assigned_assignments.add(selected_assignment)
                    selected_assignment.grader_id = preselected_grader
                    logger.info('Assigned file {} submitted by {} to grader {} (student was preselected)'.format(
                        selected_assignment.filename, section[preselected_student].name,
                        graders[preselected_grader].name))
            # step 4: satisfy all exclusions
            students_with_exclusions = dict()
            for excluded_grader, excluded_student in exclusions:
                if excluded_student not in submitted_student_usc_id:
                    break
                elif excluded_student in students_with_exclusions.keys():
                    students_with_exclusions[excluded_student].append(excluded_grader)
                else:
                    students_with_exclusions[excluded_student] = [excluded_grader]

            for excluded_student in students_with_exclusions:
                grader_pool = set(graders.keys()).difference(set(students_with_exclusions[excluded_student]))
                assigned_grader = random.sample(grader_pool, 1)[0]
                self.number_of_assignments_already_given[assigned_grader] += 1
                selected_assignment = section[excluded_student].assignments[self.assignment_name]
                graders[assigned_grader].assignments_graded[self.assignment_name] \
                    .append(selected_assignment)
                assigned_assignments.add(selected_assignment)
                selected_assignment.grader_id = assigned_grader
                logger.info('Assigned file {} submitted by {} to grader {} (student had exclusions)'.format(
                    selected_assignment.filename, section[excluded_student].name,
                    graders[assigned_grader].name))

            # step 5: distribute the remaining assignments
            remaining_assignments = submitted_assignments.difference(assigned_assignments)

            for assignment in remaining_assignments:
                assigned_grader = self._get_unmaxed_grader(graders)
                graders[assigned_grader].assignments_graded[self.assignment_name] \
                    .append(assignment)
                assigned_assignments.add(assignment)
                assignment.grader_id = assigned_grader
                logger.info('Assigned file {} submitted by {} to grader {}'.format(
                    assignment.filename, section[assignment.student_id].name,
                    graders[assigned_grader].name))

            # step 6: logging
            logger.info('Completed assignments to graders\n')


            logger.info('For this assignment, graders have received the following number of files:')
            for grader_id, grader in graders.items():
                logger.info(grader.name + ': ' + str(self.number_of_assignments_already_given[grader_id]) +
                            ' during this run, ' +
                            str(len(grader.assignments_graded[self.assignment_name])) + ' overall')

            logger.info('')
            if submitted_student_usc_id != set(section.keys()):
                missing_assignment_students = set(section.keys()).difference(submitted_student_usc_id)
                logger.info('{} students did not have assignments submitted:'.format(len(missing_assignment_students)))
                for student_id in missing_assignment_students:
                    logger.info(section[student_id].name)

    def _get_unmaxed_grader(self, graders):
        # function attempts to distribute assignments roughly evenly over the course of multiple days, while still
        # respecting total number of grading slots available
        counter = 0
        while True:
            assigned_grader = random.sample(graders.keys(), 1)[0]
            # check that we aren't assigning to a grader that's already maxed
            if graders[assigned_grader].assignments_required >= \
                    len(graders[assigned_grader].assignments_graded[self.assignment_name]) + self.current_preselections.count(assigned_grader):
                # then check that we aren't assigning a disproportionate amount
                if self.number_of_assignments_already_given[assigned_grader] < \
                      self.proportional_assignments_to_grade[assigned_grader]:
                    self.number_of_assignments_already_given[assigned_grader] += 1
                    return assigned_grader
                # if we can't do that in a reasonable amount of tries, relax the disproportionate check:
                counter += 1
                if counter > 20:
                    return assigned_grader
            elif counter > 100:
                raise ValueError('Not enough grading slots available for all assignments.')

    def _clean_downloaded_filenames(self):
        # get rid of name that TurnItIn prepends and check for valid 10 digit ID
        with cd(self.assignment_folder_path):
            filelist = os.listdir()
            for filename in filelist:
                # regex finds last 10 digit element in string (if the
                # submission is anonymous, TurnItIn prepends a 10
                # digit ID completely unrelated to what we want, so
                # this is an easy solution for the moment)
                match = re.search("\d{10}(?!.*\d{10})", filename)
                if match is None:
                    print('No 10-digit USC ID found for ' + filename +
                          '. File not processed.')
                    os.remove(filename)
                else:
                    new_filename = filename[match.start():len(filename)]
                    os.rename(filename, new_filename)
                    # build a list of tuples (groupnumber, filename)
                    # for use in priority queue
                    stripped_new_filename = new_filename[11:len(new_filename)]
                    match = re.match('\d{1,2}', stripped_new_filename)
