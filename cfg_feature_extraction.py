import os
import networkx as nx
import numpy as np

from cfg_parsing import read_graph


# This is another interesting link to explain GCN (Graph Convolution Network):
# https://towardsdatascience.com/how-to-do-deep-learning-on-graphs-with-graph-convolutional-networks-7d2250723780


# The node types can be of the following types (according to Yan2019):
# 1) Code Sequence:
# -- # Numeric Constants: (assignments in our case)
# -- # Transfer Instructions:
# -- # Call Instructions: METHOD
# -- # Arithmetic Instructions: <operator>.sizeOf, <operator>.cast, <operator>.subtraction, <operator>.division
#                               <operator>.preDecrement, <operator>.minus, <operator>.addition, <operator>.preIncrement
# -- # Compare Instructions: <operator>.equals, <operator>.lessThan, <operator>.logicalNot, <operator>.conditional,
#                            <operator>.logicalOr, <operator>.logicalAnd, <operator>.greaterThan, <operator>.notEquals
# -- # Move Instructions: (not considered)
# -- # Termination Instructions: (return, exit), METHOD_RETURN, RETURN
# -- # Data Declaration Instructions: (variable declaration), <operator>.new, <operator>.assignment
# -- # Total Instructions: (not sure what would be the difference between it and the instructions in the vertex)
# 2) Vertex Structure:
# -- # Offspring (Degree)
# -- # Instructions in the Vertex

# <operator>.indirection, <operator>.addressOf
# NS_LITERAL_CSTRING, NS_SUCCEEDED, NS_ENSURE_TRUE, NS_LITERAL_STRING, NS_ASSERTION, NS_FAILED, NS_ADDREF, UNKNOWN
# pushBuffer.Append, getter_AddRefs, buffer.Append, getter_Copies

# All items have 5 or more occurrences, or they are obviously a reserved node (total of 141 node types)


def obtain_cfg_data_structures(cfg_filepath):
    A, X, cfg_nx = None, None, None
    if os.path.exists(cfg_filepath):
        graphs = read_graph(cfg_filepath)

        if graphs is not None:
            cfg_dot = graphs[0]
            cfg_nx = nx.nx_pydot.from_pydot(cfg_dot)
            # s = Source(cfg_dot, filename="test.gv", format="pdf")
            # s.view()

            # TODO what if we do a topological sorting?
            if len(cfg_nx.nodes()) > 0:
                A, node_order = convert_graph_to_adjacency_matrix(cfg_dot)
                X = obtain_attribute_matrix(cfg_nx, node_order)
    return A, X, cfg_nx


def convert_graph_to_adjacency_matrix(cfg_dot):
    cfg = nx.nx_pydot.from_pydot(cfg_dot)
    node_types = obtain_node_types(cfg_dot)

    print(node_types)

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
    return np_matrix, different_order_nodes


def obtain_attribute_matrix(cfg_nx, node_order):
    # This is a matrix with node degrees. Other attributes can be used
    # TODO Normalize this matrix
    X = np.zeros((len(node_order), 2))
    for i in range(X.shape[0]):
        X[i][0] = cfg_nx.out_degree(node_order[i])  # outdegree
        X[i][1] = cfg_nx.in_degree(node_order[i])  # indegree
    return X


def get_node_type(label):
    # remove the quotes and parenthesis
    node_type = label[2:-2]
    node_type = node_type[0:node_type.index(",")]
    return node_type


def obtain_node_types(cfg_dot):
    node_types = {}
    for node in cfg_dot.get_nodes():
        print(node.get_name(), node.get_label())
        node_type = get_node_type(node.get_label())
        if node_type not in node_types:
            node_types[node_type] = 1
        else:
            node_types[node_type] += 1
    print(node_types)
    return node_types