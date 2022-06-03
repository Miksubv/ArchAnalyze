# -*- coding: utf-8 -*-
'''
Purpose:
    Functions for constructing and operating on two collections
    of trees describing the modules in the analyzed program
    and their import dependencies.
    One collection describes the modules in the program itself
    The other collection describes the external packages that
    the program depends on.
    
    Each collection looks like this:
        {
            ("__module_description__", ModuleDescription<zeeguu>),
            ("zeeguu.api",
                 {
                     ("__module_description__", ModuleDescription<zeeguu.api>),
                     ("zeeguu.api.api",
                          {
                              ("__module_description__", ModuleDescription<zeeguu.api.api>),
                              ...
                          }
                     ("zeeguu.api.test",
                          {
                              ("__module_description__", ModuleDescription<zeeguu.test>),
                              ...
                          }
                     )                    
                  }
             ),
             ("zeeguu.core",
                  {
                      ...
                  }
             ),
             ...
        }
'''

from AAModule import AAModule
from AAFileSystem import AAFileSystem
from AAAST import AAAST
import copy

MODULE_DESCRIPTION_TAG = "__module_description__"

def init_tree_collection():
    '''
    Analyzes the folder and file structure of the target system

    Returns
    -------
    roots : collection of trees describing modules of the analyzed system
        and their import dependencies
    external_module_roots : collection of trees describing external packages
        imported by the analyzed system.
    '''
    roots = build_tree()
    external_module_roots = {}
    build_external_module_tree(roots, external_module_roots)
    return roots, external_module_roots

def get_all_module_descriptions():
    '''
    Traverses the folders and files of the target system and creates
    a ModuleDescription object for each py-file.        

    Returns
    -------
    modules : list of ModuleDescription

    '''
    modules = []
    for file in AAFileSystem.all_file_paths(".py"):
        modules.append(ModuleDescription(file))
    return modules


def build_tree():
    '''
    Create a collection of trees describing the modules that are part of the
    target system.    
    
    Returns
    -------
    roots : collection of trees

    '''
    modules = get_all_module_descriptions()
    roots = {}
    for module_description in modules:
        components = module_description.full_name.split(".")
        module_collection = roots
        for component in components:
            module_collection = module_collection.setdefault(component, {})
        module_collection.setdefault(MODULE_DESCRIPTION_TAG, module_description)
    return roots

def add_module_description_to_roots(module_description, roots):
    '''
    Add a module description to the "roots" collection of trees.
    The module full name is used a path in the appropriate tree,
    and the module_description is inserted as a value with the key MODULE_DESCRIPTION_TAG
    at the end of the path.

    Parameters
    ----------
    module_description : ModuleDescription
    roots : collection of trees

    Returns
    -------
    Modifies roots
    '''
    components = module_description.full_name.split(".")
    module_collection = roots
    for component in components:
        module_collection = module_collection.setdefault(component, {})
    module_collection.setdefault(MODULE_DESCRIPTION_TAG, module_description)

def build_external_module_tree(roots, external_module_roots):
    '''
    Construct a collection of trees describing the external packages
    imported by the modules in the target system.

    Parameters
    ----------
    roots : collection of trees
        Describes the target system.
    external_module_roots : collection of trees
        Must be empty. Returns a description of the external packages.

    Returns
    -------
    External packages returned in external_module_roots.

    '''
    for module_description in traverse_modules(roots):
        for imported_module_full_name in module_description.imports:
            imported_module_description = get_module_description(roots, imported_module_full_name)
            if imported_module_description == None:
                # Ah, an external module
                imported_module_description = get_module_description(external_module_roots, imported_module_full_name)
                if imported_module_description == None:
                    # Add a new external module description.
                    imported_module_description = ModuleDescription()
                    imported_module_description.set_as_external(imported_module_full_name)
                    add_module_description_to_roots(imported_module_description, external_module_roots)
            

def get_module_description(roots, module_full_name):
    '''
    Find the ModuleDescription for module_full_name in the "roots" collection of trees
    We allow "partial finds", in case module_full_name references something inside a py file,
    or a module that has been folded into a parent.
    
    Parameters
    ----------
    roots : collection of trees
        Can be either the system collection or the external collection
    module_full_name : string
        Full name of the module to find.

    Returns
    -------
    ModuleDescription object for the module searched for. Or None if not found.
    '''
    module_collection = roots
    components = module_full_name.split(".")
    for component in components:
        value = module_collection.get(component)
        if value == None:
            # We might be referencing something from within a py file. Try to return the module_description for the py file instead.
            # Or we might be referencing a module that have been folded into a parent. So we try to return the parent module_description.
            return module_collection.get(MODULE_DESCRIPTION_TAG)
        module_collection = value
    return module_collection.get(MODULE_DESCRIPTION_TAG) # Either it exists or we return None.

def traverse_modules(roots):
    '''
    Generator for traversing a collection of module trees.

    Parameters
    ----------
    roots : collection of trees
        Can be either the system collection or the external collection.

    Yields
    ------
    Next ModuleDescription object from the collection of trees
    '''
    for module_name, value in roots.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            yield value
        else:
            yield from traverse_modules(value)

def fold_modules(roots, external_module_roots, fold_predicate):
    '''
    Fold modules into their parent modules.
    The parent module assimilates all imports from the folded
    submodules.
    All imports to folded modules are pruned to point to the parent
    module instead.

    Parameters
    ----------
    roots : collection of trees
        Description of the target system modules
    external_module_roots : collection of trees
        Description of the external packages
    fold_predicate : function that takes a string argument and returns bool
        Input is a full module name. Output must be true for sub-modules
        that are to be folded into their parents.

    Returns
    -------
    Two collection of trees:
        The new description of the target system modules
        The new description of the external packages
    '''
    folded_roots = fold_modules_recursive(roots, "", fold_predicate)
    folded_external_module_roots = fold_modules_recursive(external_module_roots, "", fold_predicate)
    prune_imports(folded_roots, folded_external_module_roots)
    return folded_roots, folded_external_module_roots

def fold_modules_recursive(module_collection, parent_module_name, fold_predicate):
    '''
    Helper function for fold_modules.
    Processes one level of a collection of trees. I.e. one collection.
    Recursive calls itself for collection members of the collection.

    Parameters
    ----------
    module_collection : collection of trees
        One level of a collection of trees. Describes a module with children.
    parent_module_name : string
        Full module name of the parent module for the module collection.
    fold_predicate : function that takes a string argument and returns bool
        Input is a full module name. Output must be true for sub-modules
        that are to be folded into their parents.

    Returns
    -------
    folded_collection : collection of trees
        A folded version of module_collection
    '''
    folded_collection = {}
    module_description = None
    # identify module description if any:
    for module_name, value in module_collection.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            module_description = copy.copy(value)  # Copy to avoid changing the original module description
            folded_collection[module_name] = module_description
    # fold what must be folded
    for module_name, value in module_collection.items():
        if module_name != MODULE_DESCRIPTION_TAG:
            module_name_prefix = parent_module_name
            if module_name_prefix:
                module_name_prefix = module_name_prefix + "."
            full_module_name = module_name_prefix + module_name
            if fold_predicate(full_module_name):
                # don't add folded collection. Insted collect the imports and add them to the parent.
                if module_description != None:
                    folded_imports = collect_folded_imports(value)
                    combined_imports = module_description.imports.union(folded_imports)
                    cleaned_imports = discard_folded_modules(combined_imports, parent_module_name) # avoid self-dependency on the folded module
                    module_description.imports = cleaned_imports
            else:
                folded_collection[module_name] = fold_modules_recursive(value, full_module_name, fold_predicate) # value is a sub-collection. Recursively process this.

    return folded_collection

def collect_folded_imports(module_collection):
    '''
    Recursive helper function for fold_modules_recursive
    Collects the imports of all modules in a collection of trees, including those
    in the sub modules.

    Parameters
    ----------
    module_collection : collection of trees
        One level of a collection of trees. Describes a module with children.

    Returns
    -------
    folded_imports : list of string
        A list of all the collected imports.
    '''
    folded_imports = set()
    for module_name, value in module_collection.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            folded_imports = folded_imports.union(value.imports)
        else:
            folded_imports = folded_imports.union(collect_folded_imports(value)) # recursively process sub-collection
    return folded_imports

def discard_folded_modules(module_full_name_collection, folded_parent_module_full_name):
    '''
    Helper function for fold_modules_recursive
    Removes all imports to the folded sub modules from a collection of module
    names.

    Parameters
    ----------
    module_full_name_collection : list of string
        List of full module names
    folded_parent_module_full_name : string
        Full module name of the parent module for the folded sub modules

    Returns
    -------
    result : list of string
        Resulting list with the module names of the sub modules that have been
        folded removed.
    '''
    result = set()
    for full_module_name in module_full_name_collection:
        if not AAModule.module_contains_module(folded_parent_module_full_name, full_module_name):
            result.add(full_module_name)
    result.discard(folded_parent_module_full_name) # module_contains_module does not detect the parent itself
    return result

def filter_modules(roots, external_module_roots, keep_predicate):
    '''
    Remove the ModuleDescriptions for modules specified by a predicate.
    Also remove imports to them.

    Parameters
    ----------
    roots : collection of trees
        Description of the target system modules
    external_module_roots : collection of trees
        Description of the external packages
    keep_predicate : function that takes a string argument and returns bool
        Input is a full module name. Output must be true for modules
        that are NOT to be removed.

    Returns
    -------
    Two collection of trees:
        The new description of the target system modules
        The new description of the external packages
    '''
    filtered_roots = filter_modules_recursive(roots, "", keep_predicate)
    filtered_external_module_roots = filter_modules_recursive(external_module_roots, "", keep_predicate)
    prune_imports(filtered_roots, filtered_external_module_roots)
    return filtered_roots, filtered_external_module_roots

def filter_modules_recursive(roots, parent_module_name, keep_predicate):
    '''
    Helper function for filter_modules.
    Processes one level of a collection of trees. I.e. one collection.
    Recursive calls itself for collection members of the collection.

    Parameters
    ----------
    roots : collection of trees
        One level of a collection of trees. Describes a module with children.
    parent_module_name : string
        Full module name of the parent module for the module collection.
    keep_predicate : function that takes a string argument and returns bool
        Input is a full module name. Output must be true for sub-modules
        that are to NOT be removed

    Returns
    -------
        A filtered version of module_collection
    '''
    result = {}
    for module_name, value in roots.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            module_description = copy.copy(value)  # Copy to avoid changing the original module description
            module_description.imports = filter_module_collection(module_description.imports, keep_predicate)
            result[MODULE_DESCRIPTION_TAG] = value
        else:
            module_name_prefix = parent_module_name
            if module_name_prefix:
                module_name_prefix = module_name_prefix + "."
            full_module_name = module_name_prefix + module_name
            if not keep_predicate(full_module_name):
                value = copy.copy(value) # we do not want to modify the input. Shallow copy is intended.
                value.pop(MODULE_DESCRIPTION_TAG, None) # remove the module description if it exists. Keep doing recursive processing in case we want to keep a sub module.
            result[module_name] = filter_modules_recursive(value, full_module_name, keep_predicate)
    return result


def filter_module_collection(module_collection, keep_predicate):
    '''
    Helper function for filter_modules_recursive
    Filter a list of module names

    Parameters
    ----------
    module_collection : list of string
        List of full module names
    keep_predicate : function that takes a string argument and returns bool
        Input is a full module name. Output must be true for module names
        that are to NOT be removed

    Returns
    -------
    result : list of string
        The resulting filtered list.
    '''
    result = []
    for full_module_name in module_collection:
        if keep_predicate(full_module_name):
            result.append(full_module_name)
    return result
assert filter_module_collection(["1", "2", "3"], lambda str : str == "2") == ["2"]


# Prune the imports for all module_descriptions to account for module folding, module filtering and for
# imports of objects inside py files.
def prune_imports(roots, imported_module_roots):
    '''
    Helper function for fold_modules and filter_modules
    Prune the imports for all module_descriptions to account for module folding, module filtering and for
    imports of objects inside py files.
    Note: modifies the input.

    Parameters
    ----------
    roots : collection of trees
        Description of the target system modules
    external_module_roots : collection of trees
        Description of the external packages

    Returns
    -------
    Modifies the imports member of the ModuleDescriptions in roots and external_module_roots.
    '''
    prune_imports_in_collection(roots, roots, imported_module_roots)
    prune_imports_in_collection(imported_module_roots, roots, imported_module_roots)

def prune_imports_in_collection(module_collection, roots, imported_module_roots):
    '''
    Helper function for prune_imports
    Prunes the imports in a collection of trees

    Parameters
    ----------
    module_collection : collection of trees
        The description to prune, either the target system
        description or the imported packages description.
    roots : collection of trees
        Description of the target system modules
    external_module_roots : collection of trees
        Description of the external packages

    Returns
    -------
    Modifies the imports member of the ModuleDescriptions in module_collection.
    Note: if module_collection aliases either roorts or external_module_roots,
    the alias is modified also.
    '''
    for module_description in traverse_modules(module_collection):
        new_imports = []
        for module_import_full_name in module_description.imports:
            # lookup the name in roots and imported_module_roots. If found, keep it. Note that
            # the module found might have a truncated name (see get_module_description). This is desired.
            import_module_description = get_module_description(roots, module_import_full_name)
            if import_module_description:
                new_imports.append(import_module_description.full_name)
            else:
                import_module_description = get_module_description(imported_module_roots, module_import_full_name)
                if import_module_description:
                    new_imports.append(import_module_description.full_name)
        module_description.imports = new_imports
        
def is_module_referenced(roots, full_module_name):
    '''
    Test if a module is imported by any modules in a collection of trees.

    Parameters
    ----------
    roots : collection of trees
        E.g., either the target system description or the imported packages description.
    full_module_name : string
        Full module name of the module to find a reference to

    Returns
    -------
    bool
        Returns true if at least one module in roots imports the specified module.
    '''
    for module_description in traverse_modules(roots):
        for imported_module_full_name in module_description.imports:
            if imported_module_full_name == full_module_name:
                return True
    return False
    
# Note: modifies roots
def stript_external_imports(roots, modules_to_strip):
    '''
    Remove imports to modules not in the Zeeguu system.

    Parameters
    ----------
    roots : collection of trees
        Only makes sense for the description of the target system
    modules_to_strip : list of strings
        Full module names for the modules to strip external imports from.

    Returns
    -------
    Modifies the imports member of the ModuleDescriptions in roots.
    '''
    for full_module_name in modules_to_strip:
        module_description = get_module_description(roots, full_module_name)
        if not module_description:
            print("stript_external_imports: failed to find module_description for: " + full_module_name)
        if module_description:
            new_imports = set()
            for imported_module in module_description.imports:
                if AAModule.module_belongs_to_zeeguu_api(imported_module):
                    new_imports.add(imported_module)
            module_description.imports = new_imports


'''
    Class for collecting metadata for a module
'''            
class ModuleDescription:
    def __init__(self, full_path=None):
        if full_path:
            self.full_path = str(full_path)
            self.full_name = AAModule.module_name_from_file_path(self.full_path)
            self.local_name = AAModule.bottom_level_module(self.full_name)
            module_node = AAAST.get_ast_for_file(full_path)
            self.imports = AAAST.get_imports(module_node)
        else:
            self.full_path = ""
            self.full_name = ""
            self.local_name = ""
            self.imports = set()
    def set_as_external(self, full_name):
        self.full_name = full_name
        self.local_name = AAModule.bottom_level_module(self.full_name)
        
    def dump(self):
        print("Module: " + self.full_name + " [" + self.full_path + "] local_name: " + self.local_name)
        print("-- imports: ", end=" ")
        print(*self.imports)


def dump_modules(roots):
    for module_description in traverse_modules(roots):
        module_description.dump()

