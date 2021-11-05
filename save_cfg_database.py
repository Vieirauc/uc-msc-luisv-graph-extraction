from cfg_parsing import read_graph
import networkx as nx
import os
import pandas as pd


data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}-sample.csv"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
CFG_FILE = "CFG_filepath"


def convert_graph_to_adjacency_matrix(cfg):
    adjacency_matrix = nx.adjacency_matrix(cfg)

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
            convert_graph_to_adjacency_matrix()


def main():
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
