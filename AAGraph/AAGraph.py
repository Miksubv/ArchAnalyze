# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAModule import AAModule
import networkx as nx

# Create a graph with all modules and dependencies between them
def dependencies_graph(modules):
    G = nx.Graph()
    for module in modules:
        module_name = module.full_name
        if module_name not in G.nodes:
            G.add_node(module_name)
        for each in module.imports:
            G.add_edge(module_name, each)
    return G

# Create a graph with directed dependencies
def dependencies_digraph(modules):
    G = nx.DiGraph()
    for module in modules:
        module_name = module.full_name
        if module_name not in G.nodes:
            G.add_node(module_name)
        for each in module.imports:
            G.add_edge(module_name, each)
    return G

def system_only_dependencies_digraph(modules):
    G = nx.DiGraph()
    for module in modules:
        module_name = module.full_name
        if module_name not in G.nodes:
            G.add_node(module_name)
#    print("+++++++++++++++++++++++++++++++++++++++++++++++")
#    print("All known nodes:")
#    for node in G.nodes():
#        print(node)
    for module in modules:
        module_name = module.full_name
        for each in module.imports:
            if G.has_node(each):
#                print("Adding " + each)
                G.add_edge(module_name, each)
#            else:
#                print("Rejected: "+ each)
    return G

def dump_digraph(G):
    print(".................................................")
    print("Dumping digraph")
    print("Nodes:")
    for node in G.nodes():
        print(node)
    print("Edges:")
    for edge in G.edges():
        print("From " + edge[0] + " To " + edge[1])

def rest_api_digraph(modules):
    r_a_name = "Rest API"
    G = nx.DiGraph()
    G.add_node(r_a_name)
    for module in modules:
        for route in module.rest_api_routes:
            print("Adding" + module.full_name)
            G.add_node(module.full_name)
            if route[0] == "GET":
                G.add_edge(module.full_name, r_a_name)
            if route[0] == "POST":
                G.add_edge(r_a_name, module.full_name)
    return G
            
            
# a filter takes an DG as input and returns another DG
def keep_nodes(inputGraph, condition):
    result = nx.DiGraph()

    for each in inputGraph.edges():
        src = each[0]
        dst = each[1]

        if (condition(src)):
          result.add_node(src)

        if (condition(dst)):
          result.add_node(dst)
          
        if (condition(src) and condition(dst)):
          result.add_edge(src, dst)
          
    return result


def abstracted_to_top_level(G, depth=1):
    aG = nx.DiGraph()
    for each in G.nodes():
        aG.add_node(AAModule.top_level_module(each, depth))
    for each in G.edges():
        src = AAModule.top_level_module(each[0], depth)
        dst = AAModule.top_level_module(each[1], depth)

        if src != dst:
          aG.add_edge(src, dst)
          
    return aG


def does_node_belong_to_module(full_node_name, full_module_name):
    return full_node_name.startswith(full_module_name + ".")

def select_nodes_from_module(G, full_module_name):
    return keep_nodes(G, lambda node : does_node_belong_to_module(node, full_module_name))
        