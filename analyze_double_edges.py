from cfg_extraction_constants import CFG_FILE
from cfg_parsing import read_graph
#import networkx as nx
import os
import pandas as pd

projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}.csv"


def analyze_double_edge(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)
    df = df[df[CFG_FILE].notnull()]

    two_edges_nodes = 0
    total_cfgs = 0
    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]

        cfg_filepath_parts = cfg_filepath.split("/")
        cfg_filename = cfg_filepath_parts[-1]
        repository_directory = cfg_filepath_parts[-2]
        output_commit = cfg_filepath_parts[-3]
        base_directory = "/".join(cfg_filepath_parts[0:-4])

        reduced_cfg_path = os.path.join(
            base_directory, "{}-reduced".format(project), output_commit, repository_directory, cfg_filename)
        #print(reduced_cfg_path)

        graphs = read_graph(reduced_cfg_path)

        if graphs is not None:
            cfg_dot = graphs[0]
            #cfg_nx = nx.nx_pydot.from_pydot(cfg_dot)
            #print([node.get_name() for node in cfg_dot.get_nodes()])
            edges = [(edge.get_source(), edge.get_destination()) for edge in cfg_dot.get_edges()]
            #print(edges)
            number_edges = len(edges)
            number_unduplicated_edges = len(set(edges))
            if number_edges != number_unduplicated_edges:
                print(reduced_cfg_path)
                two_edges_nodes += 1
            total_cfgs += 1
    print("total_cfgs: {}, two_edge_nodes: {}".format(total_cfgs, two_edges_nodes))

    # gecko-dev
    # total_cfgs: 254160, two_edge_nodes: 20098 (7.91%)

    # linux
    # total_cfgs: 104760, two_edge_nodes: 14846 (14.17%)



def main():
    for project in projects[3:4]:
        analyze_double_edge(project)


if __name__ == "__main__":
    main()
