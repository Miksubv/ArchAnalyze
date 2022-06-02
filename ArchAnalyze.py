# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAModule import AAModule
from AAAST import AAAST
from AAView import AAView
from AAGraph import AAGraph
from AAFileSystem import AAFileSystem
from AAHistory import AAHistory
from AAModuleTree import AAModuleTree

roots, external_module_roots = AAModuleTree.init_tree_collection()
AAModuleTree.dump_modules(roots)
AAModuleTree.dump_modules(external_module_roots)

AAView.create_top_module_view(roots, external_module_roots)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.api", [], 1)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.api.api", [], 1, ["flask"])

AAView.create_sub_module_view(roots, {}, "zeeguu.core", [], .2)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.core.model", [], 3, ["sqlalchemy"]) # excluding sqlalchemy for clarity (most zeeguu.core.model modules depend on it)

AAView.create_sub_module_view(roots, external_module_roots, "tools", [], 1)

# fold_predicate = lambda module_name : AAModule.any_module_contains_module(["zeeguu.api", "zeeguu.core", "tools"], module_name)
# folded_roots, folded_external_roots = AAModuleTree.fold_modules(roots, external_module_roots, fold_predicate)
# filter_predicate = lambda module_name : AAModule.module_belongs_to_zeeguu_api(module_name) or (AAModule.module_level(module_name) == 1 and AAModule.is_significant_external_module(module_name))
# filtered_roots, filtered_external_roots = AAModuleTree.filter_modules(folded_roots, folded_external_roots, filter_predicate)

#TG = AAGraph.dependencies_digraph_from_roots(folded_roots)
#TG = AAGraph.dependencies_digraph_from_roots(folded_external_roots)
###TG = AAGraph.dependencies_digraph_from_roots(filtered_roots)
###TG2 = AAGraph.dependencies_digraph_from_roots(filtered_roots, filtered_external_roots)
#AAView.draw_graph_with_labels(TG, (5, 5), "Top level modules")
#AAView.draw_graph_with_labels(TG, (15, 15), "Top level modules")
###AAView.draw_graph_with_weights(TG, AAView.scaled_weights_bounded(AAFileSystem.module_LOC, 0.1, 10), (20,18), "Toplevel system modules sized by LOC")
###AAView.draw_graph_with_weights(TG2, AAView.scaled_weights_bounded(AAFileSystem.module_LOC, 0.1, 10), (20,18), "Toplevel system modules sized by LOC")

# View of toplevel system modules and dependencies
#TG2 = AAGraph.abstracted_to_top_level(TG)
#AAView.draw_graph_with_labels(TG2, (20,18), "Toplevel system modules")
# View of toplevel system modules and dependencies sized by LOC
## AAView.draw_graph_with_weights(ADG2, AAFileSystem.module_LOC, (20,18), "Toplevel system modules sized by LOC")





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


abe = AAModuleTree.generate_module_node_id()

# Raw view of all top level modules and dependencies
DG = AAGraph.dependencies_digraph(modules)
ADG = AAGraph.abstracted_to_top_level(DG)
## AAView.draw_graph_with_labels(ADG, (20,18))

# View of system modules and dependencies
DG2 = AAGraph.system_only_dependencies_digraph(modules)
### AAView.draw_graph_with_labels(DG2, (20,18), "System modules")

DG3 = AAGraph.isolation_graph(modules, 3)

# View of toplevel system modules and dependencies
ADG2 = AAGraph.abstracted_to_top_level(DG2)
## AAView.draw_graph_with_labels(ADG2, (20,18), "Toplevel system modules")
# View of toplevel system modules and dependencies sized by LOC
## AAView.draw_graph_with_weights(ADG2, AAFileSystem.module_LOC, (20,18), "Toplevel system modules sized by LOC")

# View of modules under the zeeguu module
## AAView.create_weighted_submodule_view(DG, "zeeguu", 2, AAFileSystem.module_LOC, (20,18), "zeeguu submodules sized by LOC")

# View of modules under the zeeguu.core module
## AAView.create_weighted_submodule_view(DG, "zeeguu.core", 3, AAFileSystem.module_LOC, (20,18), "zeeguu.core submodules sized by LOC")
## AAView.create_bounded_weighted_submodule_view(DG, "zeeguu.core", 3, AAFileSystem.module_LOC, lambda LOC : LOC > 100, (20,18), "zeeguu.core submodules sized by LOC, constrained by LOC > 100")

# View of modules under the zeeguu.core.model module
## AAView.create_weighted_submodule_view(DG, "zeeguu.core.model", 4, AAFileSystem.module_LOC, (20,18), "zeeguu.core.model submodules sized by LOC")

# View of modules under the zeeguu.api module
## AAView.create_weighted_submodule_view(DG, "zeeguu.api", 3, AAFileSystem.module_LOC, (20,18), "zeeguu.api submodules sized by LOC")

# View of modules under the zeeguu.api.api module
## AAView.create_weighted_submodule_view(DG, "zeeguu.api.api", 4, AAView.scaled_weights(AAFileSystem.module_LOC, 5), (20,18), "zeeguu.api.api submodules sized by LOC (weights scale up 10 times)")

# View of modules under the tools module
## AAView.create_weighted_submodule_view(DG, "tools", 2, AAView.scaled_weights(AAFileSystem.module_LOC, 10), (20,18), "tools submodules sized by LOC (weights scaled up 10 times)")

print("calc churn")
#AAHistory.add_churns_for_modules(modules)
print("calc churn done")


# Attempt of a view of the rest api
# RDG = AAGraph.rest_api_digraph(modules)
# AAView.draw_graph_with_labels(RDG, (20,18))


print("################################################")
#sl = AAModule.lookup_module(modules, "student_exercises")
#sl_ast = AAAST.get_ast_for_file(sl.full_path)
#print(ast.dump(sl_ast))

print("################################################")
# AAHistory.print_churns(AAHistory.get_all_commits())

print("=======================================")
# AAModule.dump_raw_rest_api_data(modules)
print("=======================================")
# AAModule.dump_rest_routes(modules)
print("=======================================")
# AAFileSystem.dump_file_type_count()   
