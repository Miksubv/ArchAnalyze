# -*- coding: utf-8 -*-
"""
@author: mlv

Purpose:
    Functions for processing files and folders.
"""

# This specifies the location of the target system to analyse
# Warning: this must end in /
CODE_ROOT_FOLDER="C:\\Users\\mlv\\.spyder-py3\\content\\Zeeguu-API\\"

import os
from git import Repo
from pathlib import Path

cwd = os.getcwd()
# If the file exists, it means we've already downloaded
if not os.path.exists(CODE_ROOT_FOLDER):
  Repo.clone_from("https://github.com/zeeguu-ecosystem/Zeeguu-API", CODE_ROOT_FOLDER)


def get_code_root_folder():
    '''
    Get the root folder for the target system.

    Returns
    -------
    string
        Full folder path.
    '''
    return CODE_ROOT_FOLDER


def file_path(file_name):
    '''
    Get a file path w/o having to always provide the /content/Zeeguu-API/ prefix  

    Parameters
    ----------
    file_name : string
        File path relative to the target system root

    Returns
    -------
    string
        Full file path.
    '''
    return CODE_ROOT_FOLDER+file_name
assert (file_path("zeeguu_core\\model\\user.py") == "C:\\Users\\mlv\\.spyder-py3\\content\\Zeeguu-API\\zeeguu_core\\model\\user.py")


def module_name_from_file_path(full_path):
    '''
    Extracting a module name from a file name
    # e.g. ../zeeguu/core/model/user.py -> zeeguu.core.model.user

    Parameters
    ----------
    full_path : string
        Full file path of the module.

    Returns
    -------
    string
        full module name of the module.
    '''
    file_name = full_path[len(CODE_ROOT_FOLDER):]
    file_name = file_name.replace("\\__init__.py","")
    file_name = file_name.replace("\\",".")
    file_name = file_name.replace(".py","")
    return file_name
assert 'zeeguu_core.model.user' == module_name_from_file_path(file_path('zeeguu_core\\model\\user.py'))


def all_file_paths(extension = ""):
    '''
    Get all file paths in a folder structure for files with a specified file extension.

    Parameters
    ----------
    extension : string, optional
        File extension for the desired file type. E.g. "py". The default is "".

    Returns
    -------
    A collection of paths.
    '''
    return Path(CODE_ROOT_FOLDER).rglob("*" + extension)


def LOC(file_path):
    '''
    Count the lines in a file.

    Parameters
    ----------
    file_path : file path
        File to measure.

    Returns
    -------
    int
        Number of lines in the file.
    '''
    return sum([1 for line in open(file_path)])


def module_LOC(module_name):
    '''
    Abstraction by aggregating metrics to the module level
    This is a bit of a hack which uses the rglob to iterate
    over all the files and uses the file prefix to assume 

    Parameters
    ----------
    module_name : string
        full module name.

    Returns
    -------
    int
        Cummulative number of lines.
    '''
    size = 0
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")

    for file in files:
        file_path = str(file)
        full_module_name = module_name_from_file_path(file_path)
        if full_module_name.startswith(module_name + '.'):
            size += LOC(file_path)

    return size

'''
def count_file_types():
    file_type_count = dict()    
    for path in Path(CODE_ROOT_FOLDER).rglob("*.*"):
        filename, file_extension = os.path.splitext(path)
        if file_extension in file_type_count:
            file_type_count[file_extension] += 1
        else:
            file_type_count[file_extension] = 1
    return file_type_count

def dump_file_type_count():
    print("Number of files with different file extensions")
    file_type_count = sorted(count_file_types().items(), key=lambda x: x[1], reverse=True)
    for item in file_type_count:
        print(item[0] + ": " + str(item[1]))

'''