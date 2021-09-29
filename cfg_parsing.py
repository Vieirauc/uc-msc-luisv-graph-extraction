import os
import pydot


def read_graph(cfg_directory, filename):
    graphs = pydot.graph_from_dot_file(os.path.join(cfg_directory, filename))
    graph = graphs[0]
    print(filename, graph.get_name())
    return graph.get_name()
    #print(graph.get_name().replace('"', ''), function_name)
    #if function_name == graph.get_name().replace('"', ''):
    #    print("ENCONTROU! ************************")
    #print(graph.get_edge_list())
    #for edge in graph.get_edge_list():
    #    print(edge)


def map_cfg_per_function(cfg_directory):
    map_cfg = {}
    for file in os.listdir(cfg_directory):
        if file.endswith(".cfg"):
            function_graph_name = read_graph(cfg_directory, file)
            map_cfg[function_graph_name] = file
    print(map_cfg)
    print(len(map))
    return map_cfg
