# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2019 raka2407
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import pandas as pd


def add_tc_row_with_type_as_test_manual(octane_tc_df, name, description):
    if octane_tc_df.empty:
        unique_id = 1
        tc_row_as_test_manual_list = [unique_id]  # unique_id
    else:
        unique_id = octane_tc_df.index.max() + 1
        tc_row_as_test_manual_list = [unique_id]  # unique_id
    tc_row_as_test_manual_list.append('test_manual')  # type
    tc_row_as_test_manual_list.append(name)  # name
    tc_row_as_test_manual_list.append('')  # step_type
    tc_row_as_test_manual_list.append(description)  # description
    tc_row_as_test_manual_list.append('')  # step_description
    tc_row_as_test_manual_list.append('')  # test_type
    tc_row_as_test_manual_list.append('')  # product_areas
    tc_row_as_test_manual_list.append('')  # covered_content
    tc_row_as_test_manual_list.append('')  # designer
    tc_row_as_test_manual_list.append('')  # estimated_duration
    tc_row_as_test_manual_list.append('')  # owner
    if octane_tc_df.empty:
        octane_tc_df.loc[1] = tc_row_as_test_manual_list
    else:
        octane_tc_df.loc[octane_tc_df.index.max() + 1] = tc_row_as_test_manual_list
    return unique_id


def add_tc_row_with_type_as_step(octane_tc_df, row_type, step_description):
    tc_row_as_step_list = [octane_tc_df.index.max() + 1]  # unique_id
    tc_row_as_step_list.append('step')  # type
    tc_row_as_step_list.append('')  # name
    if row_type == 'Simple':
        tc_row_as_step_list.append('Simple')  # step_type
    if row_type == 'Validation':
        tc_row_as_step_list.append('Validation')  # step_type
    tc_row_as_step_list.append('')  # description
    if row_type == 'Simple':
        tc_row_as_step_list.append(step_description)  # step_description
    if row_type == 'Validation':
        tc_row_as_step_list.append(step_description)  # step_description
    tc_row_as_step_list.append('')  # test_type
    tc_row_as_step_list.append('')  # product_areas
    tc_row_as_step_list.append('')  # covered_content
    tc_row_as_step_list.append('')  # designer
    tc_row_as_step_list.append('')  # estimated_duration
    tc_row_as_step_list.append('')  # owner
    octane_tc_df.loc[octane_tc_df.index.max() + 1] = tc_row_as_step_list


def add_ts_row_with_type_as_test_suite(octane_ts_df, name):
    if octane_ts_df.empty:
        ts_row_as_test_suite_list = [1]  # unique_id
    else:
        ts_row_as_test_suite_list = [octane_ts_df.index.max() + 1]  # unique_id
    ts_row_as_test_suite_list.append('test_suite')  # type
    ts_row_as_test_suite_list.append(name)  # name
    ts_row_as_test_suite_list.append('')  # test_id
    ts_row_as_test_suite_list.append('')  # product_areas
    ts_row_as_test_suite_list.append('')  # covered_content
    ts_row_as_test_suite_list.append('')  # designer
    ts_row_as_test_suite_list.append('')  # description
    ts_row_as_test_suite_list.append('')  # owner
    ts_row_as_test_suite_list.append('')  # user_tags
    ts_row_as_test_suite_list.append('')  # aaa_udf
    if octane_ts_df.empty:
        octane_ts_df.loc[1] = ts_row_as_test_suite_list
    else:
        octane_ts_df.loc[octane_ts_df.index.max() + 1] = ts_row_as_test_suite_list


def add_ts_row_with_type_as_test_manual(octane_ts_df, test_id):
    ts_row_as_test_manual_list = [octane_ts_df.index.max() + 1]  # unique_id
    ts_row_as_test_manual_list.append('test_manual')  # type
    ts_row_as_test_manual_list.append('')  # name
    ts_row_as_test_manual_list.append(test_id)  # test_id
    ts_row_as_test_manual_list.append('')  # product_areas
    ts_row_as_test_manual_list.append('')  # covered_content
    ts_row_as_test_manual_list.append('')  # designer
    ts_row_as_test_manual_list.append('')  # description
    ts_row_as_test_manual_list.append('')  # owner
    ts_row_as_test_manual_list.append('')  # user_tags
    ts_row_as_test_manual_list.append('')  # aaa_udf
    if octane_ts_df.empty:
        octane_ts_df.loc[1] = ts_row_as_test_manual_list
    else:
        octane_ts_df.loc[octane_ts_df.index.max() + 1] = ts_row_as_test_manual_list


def write_df_to_excel(target_file, octane_tc_df, octane_ts_df):
    with pd.ExcelWriter(target_file) as writer:
        octane_tc_df.to_excel(writer, sheet_name='manual tests', index=False)
        octane_ts_df.to_excel(writer, sheet_name='test suites', index=False)
    print("Transformation completed")


def transform_ard_to_octane(options):
    if options.path is None and options.input is None and options.output is None:
        exit("Use -h for Help")
    if options.path is None:
        exit("Path of input and output files is missing, can be passed using -p")
    elif options.input is None:
        exit("ARD file name is missing, can be passed using -i")
    elif options.output is None:
        exit("Octane file name is missing, can be passed using -o")
    else:
        path = os.path.abspath(os.path.expanduser(options.path))
        source_file_name = options.input
        target_file_name = options.output
        source_file = os.path.join(path, source_file_name)
        target_file = os.path.join(path, target_file_name)
        octane_tc_df = pd.DataFrame(
            columns=['unique_id', 'type', 'name', 'step_type', 'description', 'step_description', 'test_type',
                     'product_areas', 'covered_content', 'designer', 'estimated_duration', 'owner'])
        octane_ts_df = pd.DataFrame(
            columns=['unique_id', 'type', 'name', 'test_id', 'product_areas', 'covered_content', 'designer',
                     'description', 'owner', 'user_tags', 'aaa_udf'])

        print("Transformation started.....please wait")
        ard_df = pd.read_excel(source_file)
        ard_extracted_df = ard_df[['Test Name', 'Description', 'Step Description', 'Expected Result', 'Test Suite']]

        # Iterate through ARD data frame
        for index, row in ard_extracted_df.iterrows():
            # Find if row['Test Name'] exists in DF; ignore if exists; add to DF with incremented index
            if row['Test Name'] not in octane_tc_df.values:
                # Row with type as 'test_manual'
                unique_id = add_tc_row_with_type_as_test_manual(octane_tc_df, row['Test Name'], row['Description'])

                if row['Test Suite'] not in octane_ts_df.values:
                    add_ts_row_with_type_as_test_suite(octane_ts_df, row['Test Suite'])
                add_ts_row_with_type_as_test_manual(octane_ts_df, unique_id)

            # Row with type as 'step' and step_type as 'Simple'
            add_tc_row_with_type_as_step(octane_tc_df, "Simple", row['Step Description'])

            # Row with type as 'step' and step_type as 'Validation'
            add_tc_row_with_type_as_step(octane_tc_df, "Validation", row['Expected Result'])

        write_df_to_excel(target_file, octane_tc_df, octane_ts_df)


def transform_alm_to_octane(options):
    if options.path is None and options.input is None and options.output is None:
        exit("Use -h for Help")
    if options.path is None:
        exit("Path of input and output files is missing, can be passed using -p")
    elif options.input is None:
        exit("ALM file name is missing, can be passed using -i")
    elif options.output is None:
        exit("Octane file name is missing, can be passed using -o")
    else:
        path = os.path.abspath(os.path.expanduser(options.path))
        source_file_name = options.input
        target_file_name = options.output
        source_file = os.path.join(path, source_file_name)
        target_file = os.path.join(path, target_file_name)
        octane_tc_df = pd.DataFrame(
            columns=['unique_id', 'type', 'name', 'step_type', 'description', 'step_description', 'test_type',
                     'product_areas', 'covered_content', 'designer', 'estimated_duration', 'owner'])
        octane_ts_df = pd.DataFrame(
            columns=['unique_id', 'type', 'name', 'test_id', 'product_areas', 'covered_content', 'designer',
                     'description', 'owner', 'user_tags', 'aaa_udf'])

        print("Transformation started.....please wait")
        alm_df = pd.read_excel(source_file)
        alm_extracted_df = alm_df[['Test Name', 'Description', 'Action', 'Expected Result']]

        # Iterate through ARD data frame
        for index, row in alm_extracted_df.iterrows():
            # Find if row['Test Name'] exists in DF; ignore if exists; add to DF with incremented index
            if row['Test Name'] not in octane_tc_df.values:
                # Row with type as 'test_manual'
                unique_id = add_tc_row_with_type_as_test_manual(octane_tc_df, row['Test Name'], row['Description'])

            # Row with type as 'step' and step_type as 'Simple'
            add_tc_row_with_type_as_step(octane_tc_df, "Simple", row['Action'])

            # Row with type as 'step' and step_type as 'Validation'
            add_tc_row_with_type_as_step(octane_tc_df, "Validation", row['Expected Result'])

        write_df_to_excel(target_file, octane_tc_df, octane_ts_df)
