import ast
import os
import networkx as nx
import numpy as np
import pandas as pd

from cfg_extraction_constants import CFG_FILE, LABEL
from cfg_parsing import read_graph
from save_cfg_features import write_cfgs_to_file


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

statements_cfg_folder = "statements-cfg-output"
reduced_cfg_folder = "reduced-cfg-output"

data_directory = "output-reduced-cfg-data"
file_cfg_data_mask = "functions-{}-reduced-cfg-sample.csv"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]


def obtain_cfg_data_structures(cfg_filepath, statements_filepath=None):
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
                X = obtain_attribute_matrix(cfg_nx, node_order, statements_filepath)
    return A, X, cfg_nx


def convert_graph_to_adjacency_matrix(cfg_dot):
    cfg = nx.nx_pydot.from_pydot(cfg_dot)
    #node_types = obtain_node_types(cfg_dot)

    #print(node_types)

    #adjacency_matrix = nx.adjacency_matrix(cfg)
    #print(type(adjacency_matrix))
    #print(adjacency_matrix)

    #np_matrix = nx.to_numpy_matrix(cfg, nodelist=cfg.nodes())
    #print(np_matrix)
    #print(cfg.nodes())

    different_order_nodes = list(cfg.nodes())
    head = different_order_nodes.pop(-2)
    different_order_nodes.insert(0, head)
    #print(different_order_nodes)
    np_matrix = nx.to_numpy_matrix(cfg, nodelist=different_order_nodes)
    #print(np_matrix)
    return np_matrix, different_order_nodes


def obtain_statements(statements_filepath):
    with open(statements_filepath) as f:
        node_statements = f.readlines()

    statement_count = {}
    for i in range(len(node_statements)):
        node = node_statements[i]
        space_index = node.index(" ")
        node_label = node[0:space_index]
        str_statements = node[space_index + 1:].replace("\n", "")

        # to read the string list, we need to use "ast"
        # str_list  = ['(RETURN,return rv;,return rv;)']
        statements = ast.literal_eval(str_statements)

        statement_count[node_label] = len(statements)
    return statement_count


def obtain_attribute_matrix(cfg_nx, node_order, statements_filepath):
    # This is a matrix with node degrees. Other attributes can be used
    # TODO Normalize this matrix

    cfg_order = len(node_order)  # number of nodes in the CFG
    if statements_filepath is None:
        statements = {node_label: 1 for node_label in node_order}
    else:
        statements = obtain_statements(statements_filepath)

    X = np.zeros((cfg_order, 3))
    for i in range(X.shape[0]):
        X[i][0] = cfg_nx.out_degree(node_order[i])  # outdegree
        X[i][1] = cfg_nx.in_degree(node_order[i])  # indegree
        X[i][2] = statements[node_order[i]]  # number of statements

    if statements_filepath is None:
        # removes the column with the number of statements per node
        X = np.delete(X, 2, 1)
    return X


def get_node_type(label):
    # remove the quotes and parenthesis
    node_type = label[2:-2]
    node_type = node_type[0:node_type.index(",")]
    return node_type


def obtain_node_types(cfg_dot):
    node_types = {}
    for node in cfg_dot.get_nodes():
        node_label = node.get_label()
        print(node.get_name(), node_label)
        if node_label is not None:
            node_type = get_node_type(node_label)
            if node_type not in node_types:
                node_types[node_type] = 1
            else:
                node_types[node_type] += 1
    print(node_types)
    return node_types


def obtain_reduced_statement_filepath(cfg_filepath):
    cfg_filepath_parts = cfg_filepath.split("/")

    cfg_filename = cfg_filepath_parts[-1]
    cfg_name = cfg_filename[:cfg_filename.index(".dot")]
    repository_directory = cfg_filepath_parts[-2]
    output_commit = cfg_filepath_parts[-3]
    project = cfg_filepath_parts[-4]
    base_directory = "/".join(cfg_filepath_parts[0:-4])

    cfg_reduced_filepath = os.path.join(base_directory, "{}-reduced".format(project),
                                        output_commit, repository_directory, "{}.dot".format(cfg_name))
    statements_filepath = os.path.join(base_directory, "{}-statements".format(project),
                                       output_commit, repository_directory, "{}.txt".format(cfg_name))
    return cfg_reduced_filepath, statements_filepath


def read_cfg_file(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)
    df = df[df[CFG_FILE].notnull()]

    dataset_samples = []
    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]
        cfg_reduced_filepath, statements_filepath = obtain_reduced_statement_filepath(cfg_filepath)

        A, X, cfg_nx = obtain_cfg_data_structures(cfg_reduced_filepath, statements_filepath)

        if A is not None:
            dataset_samples.append((cfg_reduced_filepath, row[LABEL], A.shape[0],
                                    list(A.getA1().flatten()), list(X.flatten())))

        if (index + 1) % 10 == 0:
            write_cfgs_to_file(project, dataset_samples)

    write_cfgs_to_file(project, dataset_samples)


def main():
    # This is just a sample for the feature extraction of the reduced CFG already
    cfg_name = "6-cfg"
    cfg_filepath = os.path.join(reduced_cfg_folder, "{}.dot".format(cfg_name))
    statements_filepath = os.path.join(statements_cfg_folder, "{}.txt".format(cfg_name))

    A, X, cfg_nx = obtain_cfg_data_structures(cfg_filepath, statements_filepath)
    #print(A)
    #print(X)

    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
