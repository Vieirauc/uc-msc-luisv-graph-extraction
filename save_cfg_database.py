from cfg_parsing import read_graph
from graphviz import Source
import networkx as nx
import numpy as np
import os
import pandas as pd

import dgl
import torch as th
import torch.nn as nn
from dgl.nn import SortPooling


data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}-sample.csv"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
CFG_FILE = "CFG_filepath"


# The node types can be of the following types (according to Yan2019):
# 1) Code Sequence:
# -- # Numeric Constants: assignments in our case
# -- # Transfer Instructions:
# -- # Call Instructions:
# -- # Arithmetic Instructions:
# -- # Compare Instructions:
# -- # Move Instructions: not considered
# -- # Termination Instructions: return, exit
# -- # Data Declaration Instructions: variable declaration
# -- # Total Instructions: (not sure what would be the differece between it and the instructions in the vertex)
# 2) Vertex Structure:
# -- # Offspring (Degree)
# -- # Instructions in the Vertex


def get_node_type(label):
    print(label)
    # remove the quotes and parenthesis
    node_type = label[2:-2]
    node_type = node_type[0:node_type.index(",")]
    return node_type


def obtain_node_types(cfg_dot):
    node_types = []
    for node in cfg_dot.get_nodes():
        print(node.get_name(), node.get_label())
        node_types.append(get_node_type(node.get_label()))
    print(node_types)
    node_types = set(node_types)
    return node_types


def convert_graph_to_adjacency_matrix(cfg_dot):
    cfg = nx.nx_pydot.from_pydot(cfg_dot)
    node_types = obtain_node_types(cfg_dot)

    print(node_types)
    print(cfg.nodes())
    print(cfg.edges())

    #adjacency_matrix = nx.adjacency_matrix(cfg)
    #print(type(adjacency_matrix))
    #print(adjacency_matrix)

    #np_matrix = nx.to_numpy_matrix(cfg, nodelist=cfg.nodes())
    #print(np_matrix)
    #print(cfg.nodes())

    different_order_nodes = list(cfg.nodes())
    head = different_order_nodes.pop(-2)
    different_order_nodes.insert(0, head)
    print(different_order_nodes)
    np_matrix = nx.to_numpy_matrix(cfg, nodelist=different_order_nodes)
    print(np_matrix)
    return np_matrix


def analyze_dot_cfg(cfg):
    print(cfg)  # prints the dot file
    print(cfg.get_name())

    for node in cfg.get_nodes():
        print(node)
        print(node.get_label())
        print(node.get_name())
    for edge in cfg.get_edges():
        print(edge)
        print(edge.get_source())
        print(edge.get_destination())

    # all nodes should have the label "CFG_Node", but only the  entry node should have the label "Function"
    # CREATE(e: CFG_Node:Function
    # {name: '1000133', label: '(METHOD,nsIndexedToHTML::Create)'})

    # additional properties that a function has
    # {commit, filepath, function_name, vulnerable}

    # Regular node
    # CREATE (e:CFG_Node {name: '1000146', label:'(<operator>.new,new nsIndexedToHTML())'})

    # Create relationship (the relationship type RELTYPE can be changed)
    # MATCH
    #   (a:CFG_Node),
    #   (b:CFG_Node)
    # WHERE a.name = '1000133' AND b.name = '1000146'
    # CREATE (a)-[r:RELTYPE]->(b)
    # RETURN type(r);


def read_cfg_file(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]
        graphs = read_graph(cfg_filepath)

        if graphs is not None:
            cfg = graphs[0]
            analyze_dot_cfg(cfg)


def obtain_identity(A):
    return np.identity(A.shape[0])


def obtain_diagonal_matrix(A_tilde):
    D = np.zeros(A_tilde.shape)
    for i in range(D.shape[0]):
        D[i][i] = np.sum(A_tilde[i, :])
    return D


def obtain_attribute_matrix(A):
    # This is a matrix with node degrees. Other attributes can be used
    # TODO Normalize this matrix
    X = np.zeros((A.shape[0], 2))
    for i in range(X.shape[0]):
        X[i][0] = np.sum(A[i, :])  # outdegree
        X[i][1] = np.sum(A[:, i])  # indegree
    return X


def calculate_graph_convolution_layer(A, X, t=1):
    I = obtain_identity(A)
    A_tilde = A + I
    print(A_tilde)
    D_tilde = obtain_diagonal_matrix(A_tilde)
    print(D_tilde)

    # W: Trainable graph convolution parameters
    W1 = np.matrix([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    W2 = np.matrix([[0.0, 1.0, -2.0, 2.0], [1.0, 1.0, 7.0, -2.0], [1.0, 0.0, -1.0, 4.0]])
    W = [W1, W2]
    print(W1)
    print(W2)
    print(X)
    # Zt+1 = f(D_tilde ^-1 A_tilde Zt Wt)
    # Z0 = X
    D_inv = np.linalg.inv(D_tilde)
    print("D_inv\n", D_inv)
    D_A = np.dot(D_inv, A_tilde)
    print("D_A\n", D_A)
    D_A_X = np.dot(D_A, X)
    print("D_A_X\n", D_A_X)
    Ztp = np.dot(D_A_X, W[t-1])

    # f: nonlinear activation function (RELU)
    Ztp = np.maximum(Ztp, 0.0)
    print("Ztp{}\n".format(t), Ztp, "\n", Ztp.shape)

    # Ztp is the output activation matrix
    return Ztp


def extract_data_from_file(cfg_directory, cfg_filename):
    graph, X, Z1_t = None, None, None

    cfg_filepath = os.path.join(cfg_directory, cfg_filename)
    graphs = read_graph(cfg_filepath)

    if graphs is not None:
        cfg_dot = graphs[0]
        print(type(cfg_dot))
        # s = Source(cfg_dot, filename="test.gv", format="pdf")
        # s.view()

        # TODO what if we do a topological sorting?
        A = convert_graph_to_adjacency_matrix(cfg_dot)
        X = obtain_attribute_matrix(A)

        Z1_t = obtain_graph_convolution_layers(A, X)
        print("Z1:t of graph from file\n", Z1_t)

        cfg_nx = nx.nx_pydot.from_pydot(cfg_dot)
        graph = dgl.convert.from_networkx(cfg_nx)
    return graph, X, Z1_t


def obtain_graph_convolution_layers(A, X, max_t=2):
    Z = []
    Zi_minus1 = X
    for i in range(0, max_t):
        Zi = calculate_graph_convolution_layer(A, Zi_minus1, t=i + 1)
        Z.append(Zi)
        Zi_minus1 = Zi
    Z1_t = Z[0]
    for i in range(0, max_t - 1):
        Z1_t = np.concatenate((Z1_t, Z[i + 1]), axis=1)

    return Z1_t


def obtain_sample_data():
    A = np.matrix([[0.0, 1.0, 0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0, 1.0, 1.0],
                   [0.0, 0.0, 0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0, 0.0, 0.0]])
    X = np.matrix([[2.0, 3.0], [1.0, 5.0], [7.0, 4.0], [8.0, 9.0], [6.0, 1.0]])
    Z1_t = obtain_graph_convolution_layers(A, X)
    print(Z1_t)

    # Sample graph from Yan2019 paper
    src_ids = th.tensor([i - 1 for i in [1, 1, 2, 3, 3]])
    dst_ids = th.tensor([i - 1 for i in [2, 4, 3, 4, 5]])
    g1 = dgl.graph((src_ids, dst_ids))

    return g1, X, Z1_t


def extract_sortpooling_layer(graph, Z1_t_th):
    # https://docs.dgl.ai/en/0.6.x/api/python/nn.pytorch.html#sortpooling
    # O k aqui é o quantidade de vértices que serão utilizados.
    # No artigo Zhang2018, o valor é definido como 60% dos grafos tendo mais de k vértices
    print("before_sortpooling\n", Z1_t_th)
    sortpool = SortPooling(k=3)
    sortpool_feats = sortpool(graph, Z1_t_th)
    print("sortpool_feats\n", sortpool_feats)
    return sortpool_feats


def extract_adaptive_max_pool(Z1_t_th):

    # The adaptive max pooling allows having different kernel sizes according to the input,
    # but the output always has the same dimensions.
    m = nn.AdaptiveMaxPool1d(3)  # THIS ALMOST WORK, BUT IT HAS A DIFFERENT STRIDE IN THE PAPER!
    amp = m(Z1_t_th)
    print("amp (AdaptiveMaxPool1d)\n", amp)
    return amp


def main():
    graph, X, Z1_t = extract_data_from_file("cfg-data", "6-cfg.dot")
    Z1_t_th = th.from_numpy(Z1_t)
    extract_sortpooling_layer(graph, Z1_t_th)
    extract_adaptive_max_pool(Z1_t_th)


    graph, X, Z1_t = obtain_sample_data()
    Z1_t_th = th.from_numpy(Z1_t)
    extract_sortpooling_layer(graph, Z1_t_th)
    extract_adaptive_max_pool(Z1_t_th)

    return
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
