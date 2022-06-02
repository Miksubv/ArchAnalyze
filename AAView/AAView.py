# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAGraph import AAGraph
from AAModule import AAModule
from AAModuleTree import AAModuleTree
from AAFileSystem import AAFileSystem
import networkx as nx
import matplotlib.pyplot as plt


# a function to draw a graph
def draw_graph(G, size, **args):
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()

def draw_graph_with_labels(G, figsize=(10,10), title=""):
    plt.figure(figsize=figsize)
    if title != "":
        plt.title(title)
    nx.draw(G, with_labels=True, node_color='#00d4e9')
    plt.show()

def draw_graph_with_weights(G, module_weight, figsize=(10,10), title=""):
    # `nx.draw` can take a list of weights for the nodes
    # and then draw them with proportional areas

    node_weights = [module_weight(each) for each in G.nodes]
    my_color_map = ['#00d4e9' if AAModule.module_belongs_to_zeeguu_api(node) else 'orange' for node in G]
    my_shapes = ['o' if AAModule.module_belongs_to_zeeguu_api(node) else 'o' for node in G]
    my_edge_color = ['black' if AAModule.module_belongs_to_zeeguu_api(edge[1]) else 'lightgrey' for edge in G.edges]
    plt.figure(figsize=figsize)
    if title != "":
        plt.title(title)
    nx.draw(G,
            with_labels=True,
            node_size=node_weights,
            node_color = my_color_map,
            edge_color = my_edge_color)
#            node_color='#00d4e9')
    plt.show()

def scaled_weights(weight_fct, scale):
    return lambda node : weight_fct(node) * scale

def scaled_weights_bounded(weight_fct, scale, min_weight):
    return lambda node : scaled_weights_bounded_fct(node, weight_fct, scale, min_weight)

def scaled_weights_bounded_fct(node, weight_fct, scale, min_weight):
    weight = weight_fct(node) * scale
    if weight < min_weight:
        weight = min_weight
    return weight

def create_top_module_view(roots, external_module_roots):
    fold_predicate = lambda module_name : AAModule.any_module_contains_module(["zeeguu.api", "zeeguu.core", "tools"], module_name)
    folded_roots, folded_external_roots = AAModuleTree.fold_modules(roots, external_module_roots, fold_predicate)
    filter_predicate = lambda module_name : AAModule.module_belongs_to_zeeguu_api(module_name) or AAModule.is_significant_external_top_level_module(module_name)
    filtered_roots, filtered_external_roots = AAModuleTree.filter_modules(folded_roots, folded_external_roots, filter_predicate)

    DG = AAGraph.dependencies_digraph_from_roots(filtered_roots, filtered_external_roots)
    draw_graph_with_weights(DG, scaled_weights_bounded(AAFileSystem.module_LOC, 0.1, 10), (10, 10), "Toplevel system modules sized by LOC")

def create_sub_module_view(roots, external_module_roots, parent_module_full_name, zeeguu_modules_to_keep, weight_scale, excluded_modules = []):
    # Remove the external imports from these. Reduces clutter.
    AAModuleTree.stript_external_imports(roots, zeeguu_modules_to_keep)
    # Fold away everything lower than directly beneath zeeguu.api and
    # fold away the sub-modules to the other modules we keep
    fold_predicate = lambda module_name : AAModule.relative_module_level(parent_module_full_name, module_name) > 1 or \
        AAModule.any_module_contains_module(zeeguu_modules_to_keep, module_name)
    folded_roots, folded_external_roots = AAModuleTree.fold_modules(roots, external_module_roots, fold_predicate)
    # Only keep sub-modules to the specified module, significant external modules and individually specified zeeguu modules
    filter_predicate = lambda module_name : AAModule.module_is_direct_sub_module(parent_module_full_name, module_name) or \
        AAModule.is_significant_external_top_level_module(module_name) or \
        module_name in zeeguu_modules_to_keep
    filtered_roots, filtered_external_roots = AAModuleTree.filter_modules(folded_roots, folded_external_roots, filter_predicate)
    # Filter away unreferenced external modules (for clarity)
    filter_predicate2 = lambda module_name :  AAModule.module_belongs_to_zeeguu_api(module_name) or \
        (AAModule.is_significant_external_top_level_module(module_name) and AAModuleTree.is_module_referenced(filtered_roots, module_name)) or \
        module_name in zeeguu_modules_to_keep
    filtered_roots2, filtered_external_roots2 = AAModuleTree.filter_modules(filtered_roots, filtered_external_roots, filter_predicate2)
    # Filter away specific modules (for clarity)
    filter_predicate3 = lambda module_name : module_name not in excluded_modules
    filtered_roots3, filtered_external_roots3 = AAModuleTree.filter_modules(filtered_roots2, filtered_external_roots2, filter_predicate3)

    DG = AAGraph.dependencies_digraph_from_roots(filtered_roots3, filtered_external_roots3)
    draw_graph_with_weights(DG, scaled_weights_bounded(AAFileSystem.module_LOC, weight_scale, 10), (10, 10), "Sub modules for " + parent_module_full_name + " sized by LOC")
    


def create_weighted_submodule_view(DG, module_name, level, weights, figsize, title):
    selected_nodes_DG = AAGraph.select_nodes_from_module(DG, module_name)
    selected_toplevel_nodes_DG = AAGraph.abstracted_to_top_level(selected_nodes_DG, level)
    draw_graph_with_weights(selected_toplevel_nodes_DG, weights, figsize, title)

def create_bounded_weighted_submodule_view(DG, module_name, level, weights, weight_constrictor, figsize, title):
    selected_nodes_DG = AAGraph.select_nodes_from_module(DG, module_name)
    selected_toplevel_nodes_DG = AAGraph.abstracted_to_top_level(selected_nodes_DG, level)
    bounded_nodes_DG = AAGraph.keep_nodes(selected_toplevel_nodes_DG, lambda node : weight_constrictor(weights(node)))
    draw_graph_with_weights(bounded_nodes_DG, weights, figsize, title)

    
