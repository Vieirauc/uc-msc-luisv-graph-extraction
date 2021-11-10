from cfg_parsing import read_graph
from graphviz import Source
import networkx as nx
import numpy as np
import os
import pandas as pd


data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}-sample.csv"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
CFG_FILE = "CFG_filepath"


def convert_graph_to_adjacency_matrix(cfg_dot):
    cfg = nx.nx_pydot.from_pydot(cfg_dot)
    for node in cfg_dot.get_nodes():
        print(node.get_name(), node.get_label())
    #print(type(cfg))

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
    X = np.zeros((A.shape[0], 2))
    for i in range(X.shape[0]):
        X[i][0] = np.sum(A[i, :])  # outdegree
        X[i][1] = np.sum(A[:, i])  # indegree
        #X[i][i] = np.sum(A[i, :])
    return X


def new_main():
    cfg_filepath = os.path.join("cfg-data", "6-cfg.dot")
    graphs = read_graph(cfg_filepath)

    if graphs is not None:
        cfg_dot = graphs[0]
        print(type(cfg_dot))
        #s = Source(cfg_dot, filename="test.gv", format="pdf")
        #s.view()
        A = convert_graph_to_adjacency_matrix(cfg_dot)
        X = obtain_attribute_matrix(A)
        calculate_graph_convolution_layer(A, X)


def calculate_graph_convolution_layer(A, X, t=1):
    I = obtain_identity(A)
    A_tilde = A + I
    print(A_tilde)
    D_tilde = obtain_diagonal_matrix(A_tilde)
    print(D_tilde)
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
    Ztp1 = np.dot(D_A_X, W[t-1])
    Ztp1 = np.maximum(Ztp1, 0.0)
    print("Ztp1\n", Ztp1, "\n", Ztp1.shape)
    return Ztp1


def main():
    new_main()
    A = np.matrix([[0.0, 1.0, 0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0, 1.0, 1.0],
                   [0.0, 0.0, 0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0, 0.0, 0.0]])
    print(type(A))
    X = np.matrix([[2.0, 3.0], [1.0, 5.0], [7.0, 4.0], [8.0, 9.0], [6.0, 1.0]])
    Z1 = calculate_graph_convolution_layer(A, X)
    Z2 = calculate_graph_convolution_layer(A, Z1, t=2)
    Z1_2 = np.concatenate((Z1, Z2), axis=1)
    print(Z1_2)
    return
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
