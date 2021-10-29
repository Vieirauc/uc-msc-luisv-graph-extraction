# dot_to_json_graph.py
# http://stackoverflow.com/questions/40262441/how-to-transform-a-dot-graph-to-json-graph

# Packages needed  :
# sudo aptitude install python-networkx python-pygraphviz python-pydot
#
# Syntax :
# python dot_to_json_graph.py graph.dot

from cfg_parsing import adjust_file
import networkx as nx
from networkx.readwrite import json_graph
import json
import os

base_dot_directory = "/opt/josep"
projects = ["xen"]


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


def main():
    for project in projects:
        convert_dot_to_json(project)


if __name__ == "__main__":
    main()
