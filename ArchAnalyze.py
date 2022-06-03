# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAView import AAView
from AAModuleTree import AAModuleTree

roots, external_module_roots = AAModuleTree.init_tree_collection()
#AAModuleTree.dump_modules(roots)
#AAModuleTree.dump_modules(external_module_roots)

AAView.create_top_module_view(roots, external_module_roots)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.api", [], 1)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.api.api", [], 1, ["flask"]) # excluding flask for clarity (most zeeguu.api.api modules depend on it)

AAView.create_sub_module_view(roots, {}, "zeeguu.core", [], .2)

AAView.create_sub_module_view(roots, external_module_roots, "zeeguu.core.model", [], 3, ["sqlalchemy"]) # excluding sqlalchemy for clarity (most zeeguu.core.model modules depend on it)

AAView.create_sub_module_view(roots, external_module_roots, "tools", [], 1)

'''
The remainder of the file are not part of the report.
Just extracting statistics for explorative purposes.
'''
'''
# from AAAST import AAAST
# from AAModule import AAModule
# from AAGraph import AAGraph
# from AAFileSystem import AAFileSystem
# from AAHistory import AAHistory

# print("calc churn")
# modules = AAModule.get_all_modules()
# AAHistory.add_churns_for_modules(modules)
# print("calc churn done")

# # Attempt of a view of the rest api
# RDG = AAGraph.rest_api_digraph(modules)
# AAView.draw_graph_with_labels(RDG, (20,18))

# print("################################################")
# AAHistory.print_churns(AAHistory.get_all_commits())

# print("=======================================")
# AAModule.dump_raw_rest_api_data(modules)
# print("=======================================")
# AAModule.dump_rest_routes(modules)
# print("=======================================")
# AAFileSystem.dump_file_type_count()   
'''