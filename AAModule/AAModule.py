# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAFileSystem import AAFileSystem
from AAAST import AAAST

# extracting a module name from a file name
def module_name_from_file_path(full_path):
    # e.g. ../zeeguu_core/model/user.py -> zeeguu_core.model.user
    
    file_name = full_path[len(AAFileSystem.CODE_ROOT_FOLDER):] # remove root part of the path
    file_name = file_name.replace("\\__init__.py","") # __init__.py defines a package. The name is the folder name.
    file_name = file_name.replace("\\",".") # convert backslashes to .
    file_name = file_name.replace(".py","") # remove the extension for python files
    return file_name
assert 'zeeguu_core.model.user' == module_name_from_file_path(AAFileSystem.file_path('zeeguu_core\\model\\user.py'))
assert 'zeeguu_core.model' == module_name_from_file_path(AAFileSystem.file_path('zeeguu_core\\model\\__init__.py'))

# extracts the parent of depth X 
def top_level_module(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[:depth])
assert (top_level_module("zeeguu_core.model.util") == "zeeguu_core")
assert (top_level_module("zeeguu_core.model.util", 2) == "zeeguu_core.model")

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
        
    def dump(self):
        print("Module: " + self.full_name + " [" + self.full_path + "] toplevel: " + self.toplevel_module)
        