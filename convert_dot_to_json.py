# dot_to_json_graph.py
# http://stackoverflow.com/questions/40262441/how-to-transform-a-dot-graph-to-json-graph

# Packages needed  :
# sudo aptitude install python-networkx python-pygraphviz python-pydot
#
# Syntax :
# python dot_to_json_graph.py graph.dot

import networkx as nx
from networkx.readwrite import json_graph
import json
import os

base_dot_directory = "/opt/josep"
projects = ["xen"]


def convert_dot_to_json(project):
    project_dir = os.path.join(base_dot_directory, project)
    for directory in os.listdir(project_dir):
        print(directory)
        files = os.listdir(os.path.join(project_dir, directory))
        for filename in files[0:1]:
            dot_graph = nx.nx_pydot.read_dot(os.path.join(project_dir, directory, filename))
            print(json.dumps(json_graph.node_link_data(dot_graph)))


def main():
    for project in projects:
        convert_dot_to_json(project)


if __name__ == "__main__":
    main()
