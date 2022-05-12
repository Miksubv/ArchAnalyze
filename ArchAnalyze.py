# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAModule import AAModule
from AAAST import AAAST
from AAView import AAView
from AAGraph import AAGraph
from AAFileSystem import AAFileSystem

modules = AAModule.get_all_modules()

module_node = AAAST.get_ast_for_file(modules[0].full_path)
imports = AAAST.get_imports(module_node)
# for importa in imports:
#    print(importa)

#my_ast = AAAST.get_ast_for_file(modules[1].full_path)

import ast
# print(ast.dump(my_ast))

# print (modules[0].toplevel_module)
# print (modules[0].full_path)

# AAModule.dump_module_names(modules[:10])

# graph = AAGraph.dependencies_graph(modules)
# AAView.draw_graph(graph, (12,10), with_labels=True)



# Raw view of all top level modules and dependencies
DG = AAGraph.dependencies_digraph(modules)
ADG = AAGraph.abstracted_to_top_level(DG)
# AAView.draw_graph_with_labels(ADG, (20,18))

# View of system modules and dependencies
DG2 = AAGraph.system_only_dependencies_digraph(modules)
# AAView.draw_graph_with_labels(DG2, (20,18), "System modules")


# View of toplevel system modules and dependencies
ADG2 = AAGraph.abstracted_to_top_level(DG2)
#AAGraph.dump_digraph(ADG2)
#AAView.draw_graph_with_labels(ADG2, (20,18), "Toplevel system modules")
# view of toplevel system modules and dependencies sized by LOC
AAView.draw_graph_with_weights(ADG2, AAFileSystem.module_LOC, (20,18), "Toplevel system modules sized by LOC")


# View of modules under the zeeguu module
DG3 = AAGraph.select_nodes_from_module(DG, "zeeguu")
AAGraph.dump_digraph(DG3)

ADG3 = AAGraph.abstracted_to_top_level(DG3, 2)
AAGraph.dump_digraph(ADG3)
#AAView.draw_graph_with_weights(ADG3, AAFileSystem.module_LOC, (20,18), "zeeguu submodules sized by LOC")

# View of modules under the zeeguu module
DG4 = AAGraph.select_nodes_from_module(DG, "tools")
AAGraph.dump_digraph(DG4)
ADG4 = AAGraph.abstracted_to_top_level(DG4, 2)
AAGraph.dump_digraph(ADG4)
AAView.draw_graph_with_weights(ADG4, lambda node : AAFileSystem.module_LOC(node) * 10, (20,18), "tools submodules sized by LOC")


# Attempt of a view of the rest api
# RDG = AAGraph.rest_api_digraph(modules)
# AAView.draw_graph_with_labels(RDG, (20,18))


print("################################################")

sl = AAModule.lookup_module(modules, "student_exercises")
sl_ast = AAAST.get_ast_for_file(sl.full_path)
#print(ast.dump(sl_ast))

print("=======================================")
# AAModule.dump_raw_rest_api_data(modules)
print("=======================================")
# AAModule.dump_rest_routes(modules)
print("=======================================")
# AAFileSystem.dump_file_type_count()   
