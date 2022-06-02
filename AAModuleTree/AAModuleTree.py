# -*- coding: utf-8 -*-

from AAModule import AAModule
from AAFileSystem import AAFileSystem
from AAAST import AAAST
import copy

MODULE_DESCRIPTION_TAG = "__module_description__"

def generate_module_node_id():
    next_module_id = 0
    while True:
        yield next_module_id
        next_module_id += 1

def init_tree_collection():
    roots = build_tree()
    external_module_roots = {}
#    connect_imports(roots, external_module_roots)
    build_external_module_tree(roots, external_module_roots)
    return roots, external_module_roots

def get_all_module_descriptions():
    modules = []
    for file in AAFileSystem.all_file_paths(".py"):
        modules.append(ModuleDescription(file))
    return modules


def build_tree():
    modules = get_all_module_descriptions()
    roots = {}
    for module_description in modules:
        components = module_description.full_name.split(".")
        module_collection = roots
        for component in components:
            module_collection = module_collection.setdefault(component, {})
        module_collection.setdefault(MODULE_DESCRIPTION_TAG, module_description)
    return roots

# Add a module description to the "roots" collection of trees.
# The module full name is used a path in the appropriate tree,
# and the module_description is inserted as a value with the key MODULE_DESCRIPTION_TAG
# at the end of the path.
def add_module_description_to_roots(module_description, roots):
        components = module_description.full_name.split(".")
        module_collection = roots
        for component in components:
            module_collection = module_collection.setdefault(component, {})
        module_collection.setdefault(MODULE_DESCRIPTION_TAG, module_description)

def build_external_module_tree(roots, external_module_roots):
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
            

# Traverse the tree collection and build the imported_modules collection in the module_descriptions
# based on the module_description.imports
# Imported modules not found in the roots tree collection are added as external modules (i.e. with no file_path)
# Recursive function. "roots" must always be the top tree collection, while "module_collection" is the
# tree collection active at this stage of the recursion.
def connect_imports(roots, external_module_roots, module_collection = None, add_externals = True):
    if module_collection == None:
        module_collection = roots
    for module_name, value in module_collection.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            module_description = value
            for imported_module_full_name in module_description.imports:
                imported_module_description = get_module_description(roots, imported_module_full_name)
                if imported_module_description == None:
                    # Ah, an external module
                    imported_module_description = get_module_description(external_module_roots, imported_module_full_name)
                    if imported_module_description == None and add_externals:
                        # Add a new external module description.
                        imported_module_description = ModuleDescription()
                        imported_module_description.set_as_external(imported_module_full_name)
                        add_module_description_to_roots(imported_module_description, external_module_roots)
                if imported_module_description and (imported_module_description not in module_description.imported_modules):
                    if not imported_module_description:
                        print("what?")
                    module_description.imported_modules.append(imported_module_description) # Add a reference to the import
        else:
            connect_imports(roots, external_module_roots, value, add_externals) # value is a sub collection. Recursively connect those also.
                
   
# Lookup module_full_name in the "roots" collection of trees
# If it is not found, return None
# We allow "partial finds", in case module_full_name references something inside a py file, or a module that has been folded into a parent.
def get_module_description(roots, module_full_name):
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
    for module_name, value in roots.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            yield value
        else:
            yield from traverse_modules(value)

def fold_modules(roots, external_module_roots, fold_predicate):
    folded_roots = fold_modules_recursive(roots, "", fold_predicate)
    folded_external_module_roots = fold_modules_recursive(external_module_roots, "", fold_predicate)
    prune_imports(folded_roots, folded_external_module_roots)
#    connect_imports(folded_roots, folded_external_module_roots)
    return folded_roots, folded_external_module_roots

def fold_modules_recursive(module_collection, parent_module_name, fold_predicate):
    folded_collection = {}
    module_description = None
    # identify module description if any:
    for module_name, value in module_collection.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            module_description = copy.copy(value)  # Copy to avoid changing the original module description
            module_description.imported_modules = [] # It is easier to remove the list and rebuild it after the folding has completed.
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
                    print("!!!!!!! fold_modules_recursive: trying to fold " + full_module_name + " but there is no module description!")
                                
            else:
                folded_collection[module_name] = fold_modules_recursive(value, full_module_name, fold_predicate) # value is a sub-collection. Recursively process this.

    return folded_collection

def collect_folded_imports(module_collection):
    folded_imports = set()
    for module_name, value in module_collection.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            folded_imports = folded_imports.union(value.imports)
        else:
            folded_imports = folded_imports.union(collect_folded_imports(value)) # recursively process sub-collection
    return folded_imports

def discard_folded_modules(module_full_name_collection, folded_parent_module_full_name):
    result = set()
    for full_module_name in module_full_name_collection:
        if not AAModule.module_contains_module(folded_parent_module_full_name, full_module_name):
            result.add(full_module_name)
    result.discard(folded_parent_module_full_name) # module_contains_module does not detect the parent itself
    return result

def filter_modules(roots, external_module_roots, keep_predicate):
    filtered_roots = filter_modules_recursive(roots, "", keep_predicate)
    filtered_external_module_roots = filter_modules_recursive(external_module_roots, "", keep_predicate)
    prune_imports(filtered_roots, filtered_external_module_roots)
#    connect_imports(filtered_roots, filtered_external_module_roots, filtered_roots, False) # False -> do not readd the removed external modules
    return filtered_roots, filtered_external_module_roots

def filter_modules_recursive(roots, parent_module_name, keep_predicate):
    result = {}
    for module_name, value in roots.items():
        if module_name == MODULE_DESCRIPTION_TAG:
            module_description = copy.copy(value)  # Copy to avoid changing the original module description
            module_description.imported_modules = [] # It is easier to remove the list and rebuild it after the filtering has completed.
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
    result = []
    for full_module_name in module_collection:
        if keep_predicate(full_module_name):
            result.append(full_module_name)
    return result
assert filter_module_collection(["1", "2", "3"], lambda str : str == "2") == ["2"]

# Prune the imports for all module_descriptions to account for module folding, module filtering and for
# imports of objects inside py files.
def prune_imports(roots, imported_module_roots):
    prune_imports_in_collection(roots, roots, imported_module_roots)
    prune_imports_in_collection(imported_module_roots, roots, imported_module_roots)

def prune_imports_in_collection(module_collection, roots, imported_module_roots):
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
    for module_description in traverse_modules(roots):
        for imported_module_full_name in module_description.imports:
            if imported_module_full_name == full_module_name:
                return True
    return False
    
# Note: modifies roots
def stript_external_imports(roots, modules_to_strip):
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

            
# Class for collection metadata for a module in the system
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
        self.imported_modules = []
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

