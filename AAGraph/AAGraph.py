# -*- coding: utf-8 -*-
"""
@author: mlv

Generates networkx graphs to be used by AAView to make graph plots for display.

"""

from AAModuleTree import AAModuleTree
import networkx as nx

def dependencies_digraph_from_roots(roots, external_module_roots = {}):
    '''
    Construct a networkx DiGraph based on the modules and imports found in
    the input collection of trees.

    Parameters
    ----------
    roots : collection of trees
        Description of the target system modules
    external_module_roots : collection of trees
        Description of the external packages

    Returns
    -------
    networkx.DiGraph.
    Resulting directed graph.
    '''
    G = nx.DiGraph()
    for module_description in AAModuleTree.traverse_modules(roots):
        module_name = module_description.full_name
        if module_name in G.nodes():
            print("!!!!!!!!!!!!!!! dependencies_digraph_from_roots: Duplicate module name: " + module_name)
        G.add_node(module_name)
    for module_description in AAModuleTree.traverse_modules(external_module_roots):
        module_name = module_description.full_name
        if module_name in G.nodes():
            print("!!!!!!!!!!!!!!! dependencies_digraph_from_roots: Duplicate external module name " + module_name)
        G.add_node(module_name)
    for module_description in AAModuleTree.traverse_modules(roots):
        for imported_module_full_name in module_description.imports:
            if G.has_node(imported_module_full_name):  # Ignore imported modules not in the graph
                G.add_edge(module_description.full_name, imported_module_full_name)
    return G
    
        

def dump_digraph(G):
    '''
    Debug function.
    Print a list of all nodes and edges in a DiGraph.

    Parameters
    ----------
    G : networkx.DiGraph
        Graph to dump

    Returns
    -------
    None.
    '''
    print(".................................................")
    print("Dumping digraph")
    print("Nodes:")
    for node in G.nodes():
        print(node)
    print("Edges:")
    for edge in G.edges():
        print("From " + edge[0] + " To " + edge[1])


'''
    The remainder of this file is not used for the report.
    It contains experiments that where ultimately not used.
'''
'''
# from AAModule import AAModule

# def rest_api_digraph(modules):
#     r_a_name = "Rest API"
#     G = nx.DiGraph()
#     G.add_node(r_a_name)
#     for module in modules:
#         for route in module.rest_api_routes:
#             print("Adding" + module.full_name)
#             G.add_node(module.full_name)
#             if route[0] == "GET":
#                 G.add_edge(module.full_name, r_a_name)
#             if route[0] == "POST":
#                 G.add_edge(r_a_name, module.full_name)
#     return G

# # Create a graph with all modules and dependencies between them
# def dependencies_graph(modules):
#     G = nx.Graph()
#     for module in modules:
#         module_name = module.full_name
#         if module_name not in G.nodes:
#             G.add_node(module_name)
#         for each in module.imports:
#             G.add_edge(module_name, each)
#     return G
# # Create a graph with directed dependencies based on imports
# def dependencies_digraph(modules):
#     G = nx.DiGraph()
#     for module in modules:
#         module_name = module.full_name
#         if module_name not in G.nodes:
#             G.add_node(module_name)
#         for each in module.imports:
#             G.add_edge(module_name, each)
#     return G

# # Create a graph of modules in the system with directed dependencies
# # Dependencies on outside packages are not shown
# def system_only_dependencies_digraph(modules):
#     G = nx.DiGraph()
#     for module in modules:
#         module_name = module.full_name
#         if module_name not in G.nodes:
#             G.add_node(module_name)
# #    print("+++++++++++++++++++++++++++++++++++++++++++++++")
# #    print("All known nodes:")
# #    for node in G.nodes():
# #        print(node)
#     for module in modules:
#         module_name = module.full_name
#         for each in module.imports:
#             if G.has_node(each):
# #                print("Adding " + each)
#                 G.add_edge(module_name, each)
# #            else:
# #                print("Rejected: "+ each)
#     return G

# def isolation_graph(modules, depth):
#     G = nx.DiGraph()
#     for module in modules:
#         module_name = module.full_name
#         trunc_module_name = AAModule.top_level_module(module_name, depth)
#         if trunc_module_name not in G.nodes:
#             G.add_node(trunc_module_name)
#     # for module in modules:
#     #     module_name = module.full_name
#     #     trunc_module_name = AAModule.top_level_module(module_name, depth)
#     #     for imported_module in module.imports:
#     #         trunc_imported_module_name = AAModule.top_level_module(imported_module, depth)
#     #         if G.has_node(trunc_imported_module_name):
#     #             print("((((" + module_name + "  -> " + imported_module + " (" + trunc_module_name + " -> " +trunc_imported_module_name + ")")
#     #             import_depth = AAModule.relative_module_level(trunc_imported_module_name, imported_module)
#     #             if G.has_edge(trunc_module_name, trunc_imported_module_name):
#     #                 abe = False

# # a filter takes an DG as input and returns another DG
# def keep_nodes(inputGraph, condition):
#     result = nx.DiGraph()

#     for each in inputGraph.edges():
#         src = each[0]
#         dst = each[1]

#         if (condition(src)):
#           result.add_node(src)

#         if (condition(dst)):
#           result.add_node(dst)
          
#         if (condition(src) and condition(dst)):
#           result.add_edge(src, dst)
          
#     return result


# def abstracted_to_top_level(G, depth=1):
#     aG = nx.DiGraph()
#     for each in G.nodes():
#         aG.add_node(AAModule.top_level_module(each, depth))
#     for each in G.edges():
#         src = AAModule.top_level_module(each[0], depth)
#         dst = AAModule.top_level_module(each[1], depth)

#         if src != dst:
#           aG.add_edge(src, dst)
          
#     return aG


# def does_node_belong_to_module(full_node_name, full_module_name):
#     return full_node_name.startswith(full_module_name + ".")

# def select_nodes_from_module(G, full_module_name):
#     return keep_nodes(G, lambda node : does_node_belong_to_module(node, full_module_name))
'''                    
        