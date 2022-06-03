# -*- coding: utf-8 -*-
"""
@author: mlv

Purpose:
    Functions for parsing the syntax tree for python files.
"""

# ast package can parse Python files
import ast

def get_ast_for_file(full_path):
    '''
    Get the ast for a python file.

    Parameters
    ----------
    full_path : path
        file path to the python file

    Returns
    -------
    AST node with AST information for the python file.
    '''
    return ast.parse(open(full_path).read())


def get_imports(module_node):
    '''
    Get a list of imported modules based on the AST for a python file.
    Imported modules are extracted from "Import xxx" and "From XXX import YYY" statements

    Parameters
    ----------
    module_node : AST node
        AST node for a python file.

    Returns
    -------
    list of string
        List of full module names for imported modules.

    '''
    extractor = NodeExtractor()
    extractor.visit(module_node)
    return extractor.imports    


'''
Visitor to extract imported modules
'''
class NodeExtractor(ast.NodeVisitor):

    def __init__(self):
      self.imports = set()
      self.rest_api_routes = []

    def visit_Import(self, import_node):
        # retrieve the name from the returned object
        # normally, there is just a single alias
        for alias in import_node.names:
            self.imports.add(alias.name)
        # delegate to the default visitor
        super(NodeExtractor, self).generic_visit(import_node)
        
    def visit_ImportFrom(self, import_from_node):
        
        if import_from_node.level == 0: # imports with level 1 import from current dir. import level 2 import from the parent dir. We ignore these
            import_from_module_name = str(import_from_node.module)
            for alias in import_from_node.names:
                imported_module_name = import_from_module_name + "." + alias.name
                self.imports.add(imported_module_name)
#        else:
#            print(ast.dump(import_from_node))
        # delegate to the default visitor
        super(NodeExtractor, self).generic_visit(import_from_node)




'''
    The remainder of this file is not used for the report.
    It contains experiments that where ultimately not used.
'''
'''
# class RestApiExtractor(ast.NodeVisitor):
#     def __init__(self):
#         self.rest_api_routes = []
#     def visit_Call(self, call_node):
#         # Check if this has an attribute with a value of "api" and a keywords list including "GET" or "POST"
# #        print(ast.dump(call_node))
#         func = call_node.func
#         if type(func) is ast.Attribute:
#             value = func.value
#             if type(value) is ast.Name:
#                 value_id = value.id
#                 if(value_id == "api"):
#                     for keyword in call_node.keywords:
#                         value_list = keyword.value
#                         for element in value_list.elts:
#                             element_value = element.value
#                             if(element_value == "GET" or element_value == "POST"):
#                                 self.register_rest_api(call_node, element_value)
                            
# #            else:
# #                print("Value is not Name")
# #        else:
# #            print("Func is not Attribute")
#         super(RestApiExtractor, self).generic_visit(call_node)
#     def register_rest_api(self, call_node, api_type):
#         api_ref = ""
#         for arg in call_node.args:
#             if type(arg) == ast.Constant:
#                 api_ref = arg.value
# #        print(api_ref)
#         self.rest_api_routes.append([api_type, api_ref])

        
#     def visit_FunctionDef(self, function_def_node):
#         for decorator_node in function_def_node.decorator_list:
#             visitor = RestApiExtractor()
#             visitor.visit(decorator_node)
#             for api_route in visitor.rest_api_routes:
#                 self.rest_api_routes.append([api_route[0] , api_route[1], function_def_node.name])

# def get_rest_api(module_node):
#     extractor = NodeExtractor()
#     extractor.visit(module_node)
#     return extractor.rest_api_routes
'''