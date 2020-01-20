# -*- coding: utf-8 -*-
"""
code_searcher.code_searcher_class
~~~~~~~~~~~~

This module is consists of main class for code searching through your
code library

:copyright: © 2019 by Stanislav Prokopyev stas.prokopiev@gmail.com.
:license: MIT, see LICENSE.rst for more details.
"""
from __future__ import print_function
import time
import os

from collections import defaultdict
from collections import OrderedDict
import pkg_resources

#####
# .decorators
from code_searcher.decorators import check_type_of_arguments
#####
# .additional_functions
from code_searcher.additional_functions import \
    get_names_of_all_functions_defined_in_py_code
from code_searcher.additional_functions import \
    get_number_of_lines_in_string
from code_searcher.additional_functions import \
    get_list_modules_imported_in_py_code
from code_searcher.additional_functions import \
    get_set_names_of_all_standard_library_packages
from code_searcher.additional_functions import \
    search_code_in_the_library_common_processes
#####
# .working_with_files
from code_searcher.working_with_files import \
    get_list_str_filenames_of_all_files_with_given_extension
from code_searcher.working_with_files import \
    get_list_str_path_all_files_with_given_extension
from code_searcher.working_with_files import \
    get_file_as_string
#####


class code_searcher_class():
    """
    A class used to do search operations on whole code of project

    ...

    Attributes
    ----------
    list_str_dirs_where_to_look : list
        list most parent folders where to look for code files
    list_str_file_extensions : list
        list strings file extensions which files to explore
    dict_time_file_changed_by_path : dict
        {"path_to_file_1": float_time_when_last_modified, ...}
    dict_list_file_paths_by_ext_by_dir : dict
        dict with pathes of all initialized files
        {"folder_path_1": {"file_extension_1": [file_path_1, ...], ...}, ...}
    dict_str_file_by_path_by_ext_by_dir : dict
        {"dir_path_1": {"file_ext_1": {"file_path_1": whole_file, ..}, ..}, ..}

    Methods
    -------
    get_file_stats_of_the_code_library(bool_is_to_print=False)
        Getting string with statistics about files in the library

    get_dict_list_file_paths_by_ext_by_dir()
        Getting dict with pathes to asked files by ext by dir

    download_files()
        For all files defined in self.dict_list_file_paths_by_ext_by_dir
        download up to date versions of files (Efficient realization)

    update_files()
        Re-search for all files in the folders and download them

    search_code_in_the_library(
            str_code_to_search,
            bool_is_to_search_case_sensitive=True,
    )
        Searching some code inside whole library and
        print all occurences in nice formatted way

    search_code_in_the_library_with_re(str_re_template)
        Searching some code inside library using regular expressions

    get_number_of_lines_in_the_library()
        Getting number of not empty lines in whole library

    print_places_where_line_length_exceed_N(
            int_max_length=99,
            list_str_file_extensions=None,
    )
        Function print all places where line length exceen N symbols

    get_names_of_all_functions_defined_in_the_py_library
        Getting set names of all functions defined in the library

    get_dict_times_py_functions_used()
        Getting {function_name: times_function_used, ...}

    get_names_of_all_py_functions_defined_but_never_used()
        Getting list of functions defined inside code but never used

    get_set_str_names_of_all_py_files
        Getting set names of all .py files inside the library

    get_list_all_imported_py_modules_in_the_library
        Getting list of all modules imported in the library

    get_names_of_outer_modules_used_in_the_library()
        Getting list of all OUTER modules imported in the library
    --------------------------------------------------------------------
    --------------------------------------------------------------------
    """

    @check_type_of_arguments
    def __init__(
            self,
            list_str_dirs_where_to_look,
            list_str_file_extensions=[".py", "ipynb"],
    ):
        """
        Parameters
        ----------
        list_str_dirs_where_to_look : list
            list most parent folders where to look for code files
        list_str_file_extensions : list, optional
            list strings file extensions which files to explore
            (default is [".py", "ipynb"])
        """
        # 0) Check that as least some arguments are given
        assert list_str_dirs_where_to_look is not None, (
            "ERROR: for initializing code_searcher obj should be given \n"
            "list of most parent folders where to search files with code \n"
            "var list_str_dirs_where_to_look: SHOULD NOT BE NONE"
        )
        # 1) Initialize class variables
        # list most parent folders where to look for code files
        self.list_str_dirs_where_to_look = [
            os.path.abspath(str_dir).lower()
            for str_dir in list_str_dirs_where_to_look
        ]
        # list strings file extensions which files to explore
        self.list_str_file_extensions = list_str_file_extensions
        # {"path_to_file_1": float_time_when_last_modified, ...}
        self.dict_time_file_changed_by_path = defaultdict(float)
        print("Downloading all files (it can be a long process, please wait.)")
        float_time_start = time.time()
        # {"folder_path_1": {"file_extension_1": [file_path_1, ...], ...}, ...}
        self.dict_list_file_paths_by_ext_by_dir = \
            self.get_dict_list_file_paths_by_ext_by_dir()
        # {"dir_path_1": {"file_ext_1": {"file_path_1": whole_file, ..}, .}, .}
        # Initialize dict_str_file_by_path_by_ext_by_dir
        self.dict_str_file_by_path_by_ext_by_dir = OrderedDict()
        int_files_downloaded = self.download_files()
        float_seconds_spent = round(time.time() - float_time_start, 2)
        print(
            "{} Files were downloaded in {} seconds".format(
                int_files_downloaded,
                float_seconds_spent
            )
        )
        # # Print file statistic
        # self.get_file_stats_of_the_code_library(bool_is_to_print=True)
        # print("Search obj INITIALIZED.")

    @check_type_of_arguments
    def __repr__(self):
        """Representation of obj

        Returns
        -------
        str
            representation of the obj
        """
        str_obj_repr = ""
        str_obj_repr += (
            "This is an obj that allows you to search through "
            "your project codebase\n"
            "for getting names of available functions "
            "use help() on current obj"
            "\n\n"
        )
        str_obj_repr += "Folders to search in: \n"
        for str_dir in self.list_str_dirs_where_to_look:
            str_obj_repr += "--> " + str_dir + "\n"
        str_obj_repr += "Extensions to check: \n"
        for str_ext in self.list_str_file_extensions:
            str_obj_repr += "--> " + str_ext + "\n"
        str_obj_repr += self.get_file_stats_of_the_code_library()
        return str_obj_repr

    @check_type_of_arguments
    def get_file_stats_of_the_code_library(self, bool_is_to_print=False):
        """Getting string with statistics about files in the library

        Parameters
        ----------
        bool_is_to_print : bool, optional
            Flag if to print file statistic or just return it
            (default is False)

        Returns
        -------
        str
            File statistic of current obj
        """
        str_stats = "\n"
        str_stats += "Files Statistic of current code library:\n"
        # Print file statistic for every folder
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            str_stats_dir = ""
            str_stats_dir += "--> For folder: " + str(str_dir) + "\n"
            int_files_in_folder = 0
            int_lines_in_folder = 0
            str_stats_dir += "--> Files_found = {int_files_in_dir}  "
            str_stats_dir += "Code_lines = {int_lines_in_dir}\n"
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            # Count number of files with every extension
            for str_ext in dict_str_file_by_path_by_ext:
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                int_code_lines = 0
                for str_file_path in dict_str_file_by_path:
                    str_full_file = dict_str_file_by_path[str_file_path]
                    int_code_lines += \
                        get_number_of_lines_in_string(str_full_file)

                int_files = len(dict_str_file_by_path)
                #####
                int_files_in_folder += int_files
                int_lines_in_folder += int_code_lines
                #####
                # Add number of files with every extension to stats
                str_stats_dir += (
                    "----> {extension}:  "
                    "Files_found = {int_files};  "
                    "Code_lines = {int_lines};  "
                    "\n"
                ).format(
                    extension=str_ext,
                    int_files=int_files,
                    int_lines=int_code_lines,
                )
            str_stats += str_stats_dir.format(
                int_files_in_dir=int_files_in_folder,
                int_lines_in_dir=int_lines_in_folder,
            )
            #####
            str_stats += "=" * 79 + "\n"
        if bool_is_to_print:
            print(str_stats)
        return str_stats

    @check_type_of_arguments
    def get_dict_list_file_paths_by_ext_by_dir(self):
        """Getting dict with pathes to asked files by ext by dir

        Parameters
        ----------

        Returns
        -------
        dict
            {"folder_path_1": {"file_extension_1": [file_path_1, ..], ..}, ..}
        """
        dict_list_file_paths_by_ext_by_dir = OrderedDict()
        for str_dir_path in self.list_str_dirs_where_to_look:
            dict_list_file_paths_by_ext = defaultdict(list)
            for str_ext in self.list_str_file_extensions:
                dict_list_file_paths_by_ext[str_ext] = \
                    get_list_str_path_all_files_with_given_extension(
                        str_dir_path,
                        str_extension_to_look_for=str_ext
                    )
            dict_list_file_paths_by_ext_by_dir[str_dir_path] = \
                dict_list_file_paths_by_ext
        return dict_list_file_paths_by_ext_by_dir

    @check_type_of_arguments
    def download_files(self):
        """
        For all files defined in self.dict_list_file_paths_by_ext_by_dir
        download up to date versions of files (Efficient realization)

        Parameters
        ----------

        Returns
        -------
        int
            Number of files for which were downloaded new versions
        """
        int_new_files_downloaded = 0
        #####
        # For every folder where to look download code files
        # Only if they were updated
        for str_dir_path in self.dict_list_file_paths_by_ext_by_dir:
            dict_list_file_paths_by_ext = \
                self.dict_list_file_paths_by_ext_by_dir[str_dir_path]
            #####
            # Necessary for correct redownloading of library
            if str_dir_path in self.dict_str_file_by_path_by_ext_by_dir:
                dict_str_file_by_path_by_ext = \
                    self.dict_str_file_by_path_by_ext_by_dir[str_dir_path]
            else:
                dict_str_file_by_path_by_ext = OrderedDict()
            #####
            for str_ext in dict_list_file_paths_by_ext:
                list_str_file_paths = dict_list_file_paths_by_ext[str_ext]
                #####
                # Necessary for correct redownloading of library
                if str_ext in dict_str_file_by_path_by_ext:
                    dict_str_file_by_path = \
                        dict_str_file_by_path_by_ext[str_ext]
                else:
                    dict_str_file_by_path = OrderedDict()
                #####
                for str_f_path in list_str_file_paths:
                    # Check if file was deleted
                    # then delete it from dict_str_file_by_path
                    if not os.path.exists(str_f_path):
                        dict_str_file_by_path[str_f_path] = ""
                        continue
                    #####
                    # Check if file was modified and if so redownload it
                    float_time_file_changed = os.stat(str_f_path).st_mtime
                    float_time_file_mod_before = \
                        self.dict_time_file_changed_by_path[str_f_path]
                    if float_time_file_mod_before != float_time_file_changed:
                        dict_str_file_by_path[str_f_path] = \
                            get_file_as_string(str_f_path)
                        self.dict_time_file_changed_by_path[str_f_path] = \
                            float_time_file_changed
                        int_new_files_downloaded += 1
                dict_str_file_by_path_by_ext[str_ext] = dict_str_file_by_path
            #####
            self.dict_str_file_by_path_by_ext_by_dir[str_dir_path] = \
                dict_str_file_by_path_by_ext
        return int_new_files_downloaded

    @check_type_of_arguments
    def update_files(self):
        """Re-search for all files in the folders and download them

        Parameters
        ----------
        Returns
        -------
        """
        print("Updating all files (it can be a long process, please wait.)")
        self.dict_list_file_paths_by_ext_by_dir = \
            self.get_dict_list_file_paths_by_ext_by_dir()
        self.download_files()

    @check_type_of_arguments
    def search_code_in_the_library(
            self,
            str_code_to_search,
            bool_is_to_search_case_sensitive=True,
    ):
        """Searching some code inside whole library and
        print all occurences in nice formatted way

        Parameters
        ----------
        str_code_to_search : str
            Code to search in the library
        bool_is_to_search_case_sensitive : bool, optional
            A flag if to search cas sensitive (default is True)

        Returns
        -------
        int
            times occurences of code found in whole library
        """
        from code_searcher.additional_functions import \
            bool_simple_search_of_code
        # 0) Reload all modified files, to have right versions
        self.download_files()
        return search_code_in_the_library_common_processes(
            self.dict_str_file_by_path_by_ext_by_dir,
            bool_simple_search_of_code,
            str_code_to_search,
            bool_is_to_search_case_sensitive=bool_is_to_search_case_sensitive,
        )

    @check_type_of_arguments
    def search_code_in_the_library_with_re(
            self,
            str_re_template,
    ):
        """Searching some code inside library using regular expressions

        Parameters
        ----------
        str_code_to_search : str
            Code to search in the library
        bool_is_to_search_case_sensitive : bool, optional
            A flag if to search cas sensitive (default is True)

        Returns
        -------
        int
            times occurences of code found in whole library
        """
        from code_searcher.additional_functions import \
            bool_search_of_code_with_re
        # 0) Reload all modified files, to have right versions
        self.download_files()
        return search_code_in_the_library_common_processes(
            self.dict_str_file_by_path_by_ext_by_dir,
            bool_search_of_code_with_re,
            str_re_template,
            bool_is_to_search_case_sensitive=True,
        )

    @check_type_of_arguments
    def get_number_of_lines_in_the_library(self):
        """Getting number of not empty lines in whole library

        Returns
        -------
        int
            Number of Not empty code lines in the library
        """
        int_lines_of_code_already_found = 0
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            for str_ext in dict_str_file_by_path_by_ext:
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                for str_file_path in dict_str_file_by_path:
                    str_whole_file = dict_str_file_by_path[str_file_path]
                    int_lines_of_code_already_found += \
                        get_number_of_lines_in_string(str_whole_file)
        return int_lines_of_code_already_found

    @check_type_of_arguments
    def print_places_where_line_length_exceed_N(
            self,
            int_max_length=99,
            list_str_file_extensions=None,
    ):
        """Function print all places where line length exceen N symbols

        Parameters
        ----------
        int_max_length : int
            Max length of one code line
        list_str_file_extensions : list, optional
            List of extensions to search through only (default is None)

        Returns
        -------
        None
        """
        print(
            "Searching all places where one line length exceeds: ",
            int_max_length
        )
        # 0) Reload all modified files, to have right versions
        self.download_files()
        if not list_str_file_extensions:
            list_str_file_extensions = self.list_str_file_extensions
        # 1) If not neccesary to search case sensitive, then lower everything
        int_occurrences_found = 0
        print("=" * 79)
        # For every folder searching through all files inside folder
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            print("For folder: {folder}".format(folder=str_dir))
            for str_ext in list_str_file_extensions:
                if str_ext not in dict_str_file_by_path_by_ext:
                    print(
                        "WARNING: NO files were downloaded for extension: " +
                        str_ext
                    )
                    continue
                if len(list_str_file_extensions) > 1:
                    print("")
                print("--> For extension: {extension}".format(
                    extension=str_ext
                ))
                bool_is_entry_found_for_cur_ext = False
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                # For every file search occurences of asked code
                for str_file_path in dict_str_file_by_path:
                    str_rel_path = os.path.relpath(str_file_path, str_dir)
                    str_full_file = dict_str_file_by_path[str_file_path]
                    list_str_file_splitted = enumerate(
                        str_full_file.splitlines()
                    )
                    #####
                    # Line by line searching for asked code
                    bool_is_entry_found_for_cur_file = False
                    for int_line_num, str_line in list_str_file_splitted:
                        if len(str_line) > int_max_length:

                            if not bool_is_entry_found_for_cur_file:
                                bool_is_entry_found_for_cur_file = True
                                bool_is_entry_found_for_cur_ext = True
                                print("----> Found in: ", str_rel_path)
                            print(
                                "------> {})".format(int_occurrences_found),
                                "line:", int_line_num,
                                " Length:", len(str_line)
                            )
                            int_occurrences_found += 1
                #####
                if not bool_is_entry_found_for_cur_ext:
                    print("----> NOTHING FOUND.")
            #####
            if int_occurrences_found:
                print("=" * 79)

    @check_type_of_arguments
    def get_names_of_all_functions_defined_in_the_py_library(self):
        """Getting set names of all functions defined in the library

        Parameters
        ----------

        Returns
        -------
        set
            set names of all functions defined in the library
        """
        list_str_functions_defined_in_the_library = []
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            for str_ext in dict_str_file_by_path_by_ext:
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                for str_file_path in dict_str_file_by_path:
                    str_full_file = dict_str_file_by_path[str_file_path]
                    list_str_functions_defined_in_the_library += \
                        get_names_of_all_functions_defined_in_py_code(
                            str_full_file
                        )
        #####
        # Delete functions which starts with "__"
        list_str_functions_defined_in_the_library = [
            str_func_name
            for str_func_name in list_str_functions_defined_in_the_library
            if not str_func_name.startswith("__")
        ]
        #####
        set_str_functions_defined_in_the_library = \
            set(list_str_functions_defined_in_the_library)
        print(
            "Found functions defined: ",
            len(set_str_functions_defined_in_the_library)
        )
        return set_str_functions_defined_in_the_library

    @check_type_of_arguments
    def get_dict_times_py_functions_used(self):
        """Getting {function_name: times_function_used, ...}

        Parameters
        ----------

        Returns
        -------
        dict
            {function_name: times_function_used, ...}
        """
        defdict_times_functions_used = defaultdict(int)
        set_str_all_funcs_defined = \
            self.get_names_of_all_functions_defined_in_the_py_library()
        # For every folder searching through all files inside folder
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            for str_ext in dict_str_file_by_path_by_ext:
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                # For every file searching all occurences of function definition
                for str_filename in dict_str_file_by_path:
                    str_full_file = dict_str_file_by_path[str_filename]
                    for str_func_to_count in set_str_all_funcs_defined:
                        defdict_times_functions_used[str_func_to_count] += \
                            str_full_file.count(str_func_to_count + "(")
                        defdict_times_functions_used[str_func_to_count] += \
                            str_full_file.count("@" + str_func_to_count)
                        defdict_times_functions_used[str_func_to_count] += \
                            str_full_file.count("return " + str_func_to_count)
        #####
        # Subtract 1 from times every function used, as its function definition
        for str_func_name in defdict_times_functions_used:
            defdict_times_functions_used[str_func_name] -= 1
        return defdict_times_functions_used

    @check_type_of_arguments
    def get_names_of_all_py_functions_defined_but_never_used(self):
        """Getting list of functions defined inside code but never used

        Parameters
        ----------

        Returns
        -------
        list
            list names of never used functions inside the code library
        """
        defdict_times_functions_used = self.get_dict_times_py_functions_used()
        list_str_never_used_functions = []
        for str_func_name in defdict_times_functions_used:
            if not defdict_times_functions_used[str_func_name]:
                list_str_never_used_functions.append(str_func_name)
        print(
            "Found never used functions: ",
            len(list_str_never_used_functions)
        )
        return sorted(list_str_never_used_functions)

    @check_type_of_arguments
    def get_set_str_names_of_all_py_files(self):
        """Getting set names of all .py files inside the library

        Parameters
        ----------

        Returns
        -------
        set
            set names of all .py files inside the library
        """
        list_names_of_all_py_files_in_library = []
        for str_dir_where_to_look in self.list_str_dirs_where_to_look:
            list_names_of_all_py_files_in_library += \
                get_list_str_filenames_of_all_files_with_given_extension(
                    str_dir_where_to_look,
                    str_extension_to_look_for=".py"
                )
        return set(list_names_of_all_py_files_in_library)

    @check_type_of_arguments
    def get_list_all_imported_py_modules_in_the_library(self):
        """Getting list of all modules imported in the library

        Parameters
        ----------

        Returns
        -------
        list
            list names of all imported modules found
        """
        list_imported_modules_found = []
        for str_dir in self.dict_str_file_by_path_by_ext_by_dir:
            dict_str_file_by_path_by_ext = \
                self.dict_str_file_by_path_by_ext_by_dir[str_dir]
            for str_ext in dict_str_file_by_path_by_ext:
                dict_str_file_by_path = dict_str_file_by_path_by_ext[str_ext]
                #####
                # One by one dealing with every file
                for str_filename in dict_str_file_by_path:
                    str_full_code_of_one_py_file = \
                        dict_str_file_by_path[str_filename]
                    list_imported_modules_found += \
                        get_list_modules_imported_in_py_code(
                            str_full_code_of_one_py_file
                        )
        #####

        list_imported_modules_found = list(set(list_imported_modules_found))
        return list_imported_modules_found

    @check_type_of_arguments
    def get_names_of_outer_modules_used_in_the_library(
            self,
            bool_is_to_print_info=True
    ):
        """Getting list of all OUTER modules imported in the library

        Parameters
        ----------
        bool_is_to_print_info : bool, optional
            bool is to print versions of outer pakages (default is True)

        Returns
        -------
        dict
            dictionary with outer pakages used with versions
        """
        print("Getting list of all used outer modules in python library")
        # set_str_names_of_all_py_files = \
        #     self.get_set_str_names_of_all_py_files()
        list_imported_modules_found = \
            self.get_list_all_imported_py_modules_in_the_library()
        print(
            "Overall unique modules imported: ",
            len(list_imported_modules_found)
        )
        #####
        # Delete inner modules from all modules imported
        # list_outer_pkgs_found = []
        # for str_my_py_module in list_imported_modules_found:
        #     if str_my_py_module not in set_str_names_of_all_py_files:
        #         list_outer_pkgs_found.append(str_my_py_module)
        #####
        # Set aside all standard library packages
        set_names_of_all_std_pkgs = \
            get_set_names_of_all_standard_library_packages()

        list_outer_pkgs_found = []
        list_std_pkgs_found = []
        for str_my_py_module in list_imported_modules_found:
            if str_my_py_module in set_names_of_all_std_pkgs:
                list_std_pkgs_found.append(str_my_py_module)
            else:
                list_outer_pkgs_found.append(str_my_py_module)
        print("--> STANDARD library packages used: ", len(list_std_pkgs_found))
        if bool_is_to_print_info:
            for int_pkg_num, str_pkg_name in enumerate(list_std_pkgs_found):
                print("----> ", int_pkg_num, ")", str_pkg_name)
        #####
        print(
            "--> OUTER packages imported: ",
            len(list_outer_pkgs_found)
        )
        # Find version for each package used
        dict_outer_pkg_ver_by_pkg_name = OrderedDict()
        for str_package_name in list_outer_pkgs_found:
            try:
                dict_outer_pkg_ver_by_pkg_name[str_package_name] = \
                    pkg_resources.get_distribution(str_package_name).version
            except BaseException:
                dict_outer_pkg_ver_by_pkg_name[str_package_name] = \
                    None
        #####
        if bool_is_to_print_info:
            int_pkg_num = 0
            for str_pkg_name in dict_outer_pkg_ver_by_pkg_name:
                print(
                    "----> ", int_pkg_num, ")", str_pkg_name,
                    ": ", dict_outer_pkg_ver_by_pkg_name[str_pkg_name]
                )
                int_pkg_num += 1
        return dict_outer_pkg_ver_by_pkg_name




