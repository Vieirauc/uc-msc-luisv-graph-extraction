import os
import pydot


def read_graph():
    graphs = pydot.graph_from_dot_file(os.path.join("cfg-data", "0-pdg.dot"))
    graph = graphs[0]
    #print(graph)
    print(graph.get_name().replace('"', ''))
    #print(graph.get_name().replace('"', ''), function_name)
    #if function_name == graph.get_name().replace('"', ''):
    #    print("ENCONTROU! ************************")
    #print(graph.get_edge_list())
    #for edge in graph.get_edge_list():
    #    print(edge)


def map_cfg_per_function():
    print("map_cfg_per_function to be implemented")
    read_graph()
