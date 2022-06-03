# -*- coding: utf-8 -*-
"""
@author: mlv

Purpose:
    Mostly utility functions to analyze the module hierarchy from the module names.
    Originally collected more information about the modules, but most have moved to AModuleTree.py.
"""

from AAFileSystem import AAFileSystem

 
def module_name_from_file_path(full_path):
    '''
    Extract a module name from a file name
    E.g., ../zeeguu_core/model/user.py -> zeeguu_core.model.user

    Parameters
    ----------
    full_path : string
        full file system path of the py file.

    Returns
    -------
    string
        Full module name for the file.
    '''
    file_name = full_path[len(AAFileSystem.CODE_ROOT_FOLDER):] # remove root part of the path
    file_name = file_name.replace("\\__init__.py","") # __init__.py defines a package. The name is the folder name.
    file_name = file_name.replace("\\",".") # convert backslashes to .
    file_name = file_name.replace(".py","") # remove the extension for python files
    return file_name
assert 'zeeguu_core.model.user' == module_name_from_file_path(AAFileSystem.file_path('zeeguu_core\\model\\user.py'))
assert 'zeeguu_core.model' == module_name_from_file_path(AAFileSystem.file_path('zeeguu_core\\model\\__init__.py'))


# extracts the parent of depth X 
def top_level_module(module_name, depth=1):
    '''
    Extracts the name of a parent of a module

    Parameters
    ----------
    module_name : string
        full module name of the module.
    depth : number, optional
        The level of the parent. Use 1 for the top level, 2 for the second level,
        etc. The default is 1.

    Returns
    -------
    string
        Full module name of the parent.
    '''
    components = module_name.split(".")
    return ".".join(components[:depth])
assert (top_level_module("zeeguu_core.model.util") == "zeeguu_core")
assert (top_level_module("zeeguu_core.model.util", 2) == "zeeguu_core.model")


def module_contains_module(module_name1, module_name2):
    '''
    Test if one module is parent to another module based on their names.

    Parameters
    ----------
    module_name1 : string
        Full module name of the potential parent module.
    module_name2 : string
        Full module name of the potential child module.

    Returns
    -------
    bool
        Returns true if module 1 is parent to module 2.
        Note a module is not considered to containt itself.
    '''
    if module_name1 == module_name2:
        return False
    components1 = module_name1.split(".")
    module2_truncated_name = top_level_module(module_name2, len(components1))
    return module_name1 == module2_truncated_name
assert module_contains_module("zeeguu_core.model", "zeeguu_core.model.user")
assert module_contains_module("zeeguu_core.model", "zeeguu_core.model.user.x")
assert not module_contains_module("zeeguu_core_model", "zeeguu_core_model")
assert not module_contains_module("zeeguu_core.model.user", "zeeguu_core.model")
assert not module_contains_module("zeeguu_core.model", "zeeguu_core.model2.user")


def any_module_contains_module(module_name_list, module_name):
    '''
    Test if any of the modules in a list of modules contain a specified module.

    Parameters
    ----------
    module_name_list : list of strings
        A list full module names of the potiential parent modules.
    module_name : string
        Full module name of the potential child module

    Returns
    -------
    bool
        Returns true if any of the modules in the list is parent to module 2.
        Note a module is not considered to containt itself.
    '''
    for module_name_candidate in module_name_list:
        if module_contains_module(module_name_candidate, module_name):
            return True
    return False
assert any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu_core.model.x")
assert any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu_core.user.x")
assert any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu_core.user.x.y")
assert not any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu_core.user")
assert not any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu_core")
assert not any_module_contains_module(["zeeguu_core.model", "zeeguu_core.user"], "zeeguu.user.x")


def module_is_direct_sub_module(parent_module_full_name, candidate_module_full_name):
    '''
    Test if a module is a direct parent of another module

    Parameters
    ----------
    module_name1 : string
        Full module name of the potential parent module.
    module_name2 : string
        Full module name of the potential child module.

    Returns
    -------
    bool
        Returns true if module 1 is the immediate parent to module 2.
    '''
    if module_contains_module(parent_module_full_name, candidate_module_full_name):
        if relative_module_level(parent_module_full_name, candidate_module_full_name) == 1:
            return True
    return False


def module_level(full_module_name):
    '''
    Returns the level of a module in the module hiearchy based on its name.

    Parameters
    ----------
    full_module_name : string
        Full module name

    Returns
    -------
    int
        E.g. the level of 'zeeguu' is 1.
        The level of 'zeeguu.core' is 2.
    '''
    components = full_module_name.split(".")
    return len(components)    


def relative_module_level(module_name1, module_name2):
    '''
    Calculate how far module 2 is below module 1 in the module hierachy.

    Parameters
    ----------
    module_name1 : string
        Full module name.
    module_name2 : string
        Full module name.

    Returns
    -------
    int
        0 if the modules are identical
        -1 if module 1 is not parent to module 2.
        Otherwise the number of levels module 2 is below module 1
    '''
    if module_name1 == module_name2:
        return 0
    if not module_contains_module(module_name1, module_name2):
        return -1
    return module_level(module_name2) - module_level(module_name1)
assert relative_module_level("zeeguu_core", "zeeguu_core") == 0
assert relative_module_level("zeeguu_core", "zeeguu_core.model") == 1
assert relative_module_level("zeeguu_core", "zeeguu_core.model.user") == 2
assert relative_module_level("zeeguu_core.model.user", "zeeguu_core") == -1
assert relative_module_level("zeeguu_core.model.x", "zeeguu_core.model.y") == -1


def module_belongs_to_zeeguu_api(full_module_name):
    '''
    Very specific to the zeeguu_api system.
    Tests if a module belongs to the zeeguu_api system or if
    it is an external dependency.

    Parameters
    ----------
    full_module_name : string
        Full module name.

    Returns
    -------
    bool
        Returns true if the module belongs to zeeguu_api.
        Returns false if not (i.e., it is an external package)
    '''
    if module_contains_module("zeeguu", full_module_name):
        return True
    if module_contains_module("tools", full_module_name):
        return True
    if full_module_name in ["env_var_defs_default", "setup", "tools", "zeeguu", "zeeguu_api_dev"]:
        return True
    return False


def is_significant_external_module(full_module_name):
    '''
    Very specific to the report.
    Tests if an external package is significant
    (i.e., do we want to display it in our graph plots?)

    Parameters
    ----------
    full_module_name : string
        Full module name.

    Returns
    -------
    bool
        Returns true if the module is significant.
    '''
    significant_external_modules = ["apimux",
                           "bs4",
                           "elasticsearch",
                           "feedparser",
                           "feed_retrieval",
                           "flask",
#                           "flask_cors",
#                           "flask_monitoringdashboard",
                           "flask_sqlalchemy",
                           "langdetect",
                           "MySQLdb",
                           "newspaper",
                           "nltk",
                           "python_translators",
                           "requests",
                           "sqlalchemy",
                           "urllib",
                           "wordstats"]
    top_module_name = top_level_module(full_module_name)
    return top_module_name in significant_external_modules

def is_significant_external_top_level_module(full_module_name):
    return module_level(full_module_name) == 1 and is_significant_external_module(full_module_name)

'''
    The remainder of this file is not used for the report.
    It contains experiments that where ultimately not used.
'''
'''
from AAAST import AAAST

def bottom_level_module(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[-depth:])

# Get a list of all python modules in the system
def get_all_modules():
    modules = []
    for file in AAFileSystem.all_file_paths(".py"):
        modules.append(ModuleInfo(file))
    return modules

# Print the module info for all the given modules
def dump_modules(modules):
    for module in modules:
        module.dump()
# Print the full_name for all the given modules        
def dump_module_names(modules):
    for module in modules:
        print(module.full_name)

def lookup_module(modules, local_name):
    return next(module for module in modules if module.local_name == local_name)

def dump_raw_rest_api_data(modules):
    for module in modules:
        if module.rest_api_routes:
            print(module.full_name)
            for rest_api_route in module.rest_api_routes:
                print(rest_api_route)

def dump_rest_routes(modules):
    post_routes = []
    get_routes = []
    for module in modules:
        for rest_api_route in module.rest_api_routes:
            if rest_api_route[0] == "POST":
                post_routes.append(rest_api_route[1])
            if rest_api_route[0] == "GET":
                get_routes.append(rest_api_route[1])
    print("Rest API GET:")
    for route in get_routes:
        print(route)
    print("Rest API POST:")
    for route in post_routes:
        print(route)

# Class for collection metadata for a module in the system
class ModuleInfo:
    def __init__(self, full_path):
        self.full_path = str(full_path)
        self.full_name = module_name_from_file_path(self.full_path)
        self.toplevel_module = top_level_module(self.full_name)
        self.local_name = bottom_level_module(self.full_name)
        module_node = AAAST.get_ast_for_file(full_path)
        self.imports = AAAST.get_imports(module_node)
        self.rest_api_routes = AAAST.get_rest_api(module_node)
        self.churn = 0 # not calculated yet
        
    def dump(self):
        print("Module: " + self.full_name + " [" + self.full_path + "] toplevel: " + self.toplevel_module)
'''
