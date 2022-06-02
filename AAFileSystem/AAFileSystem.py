# -*- coding: utf-8 -*-
"""
Created on Tue May 10 16:29:29 2022

@author: mlv
"""

import os
cwd = os.getcwd()

# Let's declare a var for the path where we're going to download a repository
# Warning: this must end in /
CODE_ROOT_FOLDER="C:\\Users\\mlv\\.spyder-py3\\content\\Zeeguu-API\\"

from git import Repo
# GitPython is a library that allows us to work easily with git from Python
# https://gitpython.readthedocs.io/en/stable/tutorial.html


# If the file exists, it means we've already downloaded
if not os.path.exists(CODE_ROOT_FOLDER):
  Repo.clone_from("https://github.com/zeeguu-ecosystem/Zeeguu-API", CODE_ROOT_FOLDER)

def get_code_root_folder():
    return CODE_ROOT_FOLDER

# get a file path w/o having to always provide the /content/Zeeguu-Core/ prefix
def file_path(file_name):
    return CODE_ROOT_FOLDER+file_name

assert (file_path("zeeguu_core\\model\\user.py") == "C:\\Users\\mlv\\.spyder-py3\\content\\Zeeguu-API\\zeeguu_core\\model\\user.py")


# extracting a module name from a file name
def module_name_from_file_path(full_path):
    # e.g. ../zeeguu_core/model/user.py -> zeeguu_core.model.user
    
    file_name = full_path[len(CODE_ROOT_FOLDER):]
    file_name = file_name.replace("\\__init__.py","")
    file_name = file_name.replace("\\",".")
    file_name = file_name.replace(".py","")
    return file_name

assert 'zeeguu_core.model.user' == module_name_from_file_path(file_path('zeeguu_core\\model\\user.py'))

# get a file path w/o having to always provide the /content/Zeeguu-Core/ prefix
def file_path(file_name):
    return CODE_ROOT_FOLDER+file_name

from pathlib import Path

def all_file_paths(extension = ""):
    return Path(CODE_ROOT_FOLDER).rglob("*" + extension)

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

# the simplest possible code metric
def LOC(file_path):
    return sum([1 for line in open(file_path)])

# Abstraction by aggregating metrics to the module level
# This is a bit of a hack which uses the rglob to iterate
# over all the files and uses the file prefix to assume 
def module_LOC(module_name):
    size = 0
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")

    for file in files:
        file_path = str(file)
        full_module_name = module_name_from_file_path(file_path)
        if full_module_name.startswith(module_name + '.'):
            size += LOC(file_path)

    return size
