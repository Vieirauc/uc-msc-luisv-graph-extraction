import os
import pydot


files_with_problems = []

def read_graph(cfg_directory, filename):
    graphs = pydot.graph_from_dot_file(os.path.join(cfg_directory, filename))
    if graphs is None:
        files_with_problems.append(filename)
        return ""
    graph = graphs[0]
    print(filename, graph.get_name().replace('"', ''))
    return graph.get_name().replace('"', '')


def map_cfg_per_function(cfg_directory):
    map_cfg = {}
    files = os.listdir(cfg_directory)
    files.sort()
    for filename in files:
        if filename.endswith(".dot"):
            function_graph_name = read_graph(cfg_directory, filename)
            map_cfg[function_graph_name] = filename
    print("map_cfg ", map_cfg)
    print("len(map_cfg) ", len(map_cfg.keys()))
    print("files_with_problems ", files_with_problems)
    print("len(files_with_problems) ", len(files_with_problems))
    return map_cfg

