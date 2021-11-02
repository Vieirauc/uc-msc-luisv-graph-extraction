# dot_to_json_graph.py
# http://stackoverflow.com/questions/40262441/how-to-transform-a-dot-graph-to-json-graph

# Packages needed  :
# sudo aptitude install python-networkx python-pygraphviz python-pydot
#
# Syntax :
# python dot_to_json_graph.py graph.dot

from cfg_parsing import adjust_file, read_graph
import networkx as nx
from networkx.readwrite import json_graph
import json
import os
import pandas as pd

base_dot_directory = "/opt/josep"
commit_data_directory = "function-data"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
commit_data_mask = "{}-functions.csv"
VULNERABLE_COMMIT_HASH = "Vulnerable Commit Hash"
FILE_PATH = "File Path"
VULNERABLE_FUNCTIONS = "Vulnerable File Functions"

graph_type = "cfg"


def convert_dot_to_json(project):
    project_dir = os.path.join(base_dot_directory, project)
    wrong_files = []
    for directory in os.listdir(project_dir)[0:1]:
        print(directory)
        files = os.listdir(os.path.join(project_dir, directory))
        for filename in files:
            try:
                dot_filepath = os.path.join(project_dir, directory, filename)
                adjust_file(dot_filepath)
                dot_graph = nx.nx_pydot.read_dot(dot_filepath)
                print(json.dumps(json_graph.node_link_data(dot_graph)))
            except TypeError:
                wrong_files.append(dot_filepath)
    print("Files with problems ({}): {} ".format(len(wrong_files), wrong_files))


def directory_per_file(project):
    return project in ["glibc", "gecko-dev", "linux"]


def map_functions_to_cfg(project):
    # TODO This function aims at
    #  1) reading the DF of functions per project
    #  2) iterating over the functions of a file in a commit
    #  3) finding the corresponding CFG file (.dot) of the function
    #  4) creating a CSV file with the output, with the following fields
    #     commit, filepath, function_name, CFG_filepath, vulnerable_label
    filepath = os.path.join(commit_data_directory, commit_data_mask.format(project))
    df = pd.read_csv(filepath)
    df = df.sort_values(by=VULNERABLE_COMMIT_HASH)

    for index, row in df.iterrows():
        commit = row[VULNERABLE_COMMIT_HASH]
        filepath = row[FILE_PATH]

        filepath_directory = filepath.replace("/", "---")
        cfg_output_directory = os.path.join(base_dot_directory, project,
                                            "output-{}-{}".format(graph_type, commit),
                                            filepath_directory)

        map_function_name_cfgfile = {}
        for cfg_file in os.listdir(cfg_output_directory):
            map_function_name_cfgfile[read_graph(cfg_output_directory, cfg_file)] = cfg_file

        print(map_function_name_cfgfile)

        functions = json.loads(row[VULNERABLE_FUNCTIONS])
        for function in functions:
            # print(row["File Path"], function["Name"], function["Vulnerable"])
            function_name = function["Name"] # TODO it should be used to select the function in the map
            vulnerable = function["Vulnerable"] == "Yes"

            # TODO still pending the creation of the CSV line

        return  # finishes the execution, just to test the mechanism


def main():
    for project in projects[2:3]:
        if directory_per_file(project):
            map_functions_to_cfg(project)
        else:
            convert_dot_to_json(project)


if __name__ == "__main__":
    main()
