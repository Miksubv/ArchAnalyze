# -*- coding: utf-8 -*-
"""
@author: mlv
"""

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
    
    plt.figure(figsize=figsize)
    if title != "":
        plt.title(title)
    nx.draw(G,
            with_labels=True,
            node_size=node_weights,
            node_color='#00d4e9')
    plt.show()
