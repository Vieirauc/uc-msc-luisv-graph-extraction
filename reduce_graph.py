from cfg_parsing import read_graph
from graphviz import Source
import matplotlib.pyplot as plt
import networkx as nx
import os

cfg_directory = "cfg-data"


def reduce_graph(cfg_dot):
    print(cfg_dot)
    cfg_nx = nx.nx_pydot.from_pydot(cfg_dot)
    print(cfg_nx)
    print("indegree", cfg_nx.in_degree())
    print("outdegree", cfg_nx.out_degree())

    indegree_1 = [node for (node, indegree) in cfg_nx.in_degree() if indegree == 1]
    outdegree_1 = [node for (node, outdegree) in cfg_nx.out_degree() if outdegree == 1]

    print("indegree1 ({}): {}".format(len(indegree_1), indegree_1))
    print("outdegree1 ({}): {}".format(len(outdegree_1), outdegree_1))

    potentially_to_be_removed = [node for node in indegree_1 if node in outdegree_1]
    print("potentially_to_be_removed ({}): {}".format(len(potentially_to_be_removed), potentially_to_be_removed))

    to_be_kept_in_graph = []
    for node in potentially_to_be_removed:
        predecessor = [pred for pred in cfg_nx.nodes if node in cfg_nx[pred]][0]
        print("node", node, "predecessor", predecessor)
        if cfg_nx.out_degree[predecessor] > 1:
            # node should be kept in the graph
            to_be_kept_in_graph.append(node)
    nodes_to_be_removed = [node for node in potentially_to_be_removed if node not in to_be_kept_in_graph]
    print("nodes_to_be_removed", nodes_to_be_removed)

    s = Source(cfg_dot, filename="output-cfg-images/0-initial-graph.gv", format="pdf")
    s.view()

    for node in nodes_to_be_removed:
        cfg_dot.get_node('"{}"'.format(node))[0].set_color("blue")

    s = Source(cfg_dot, filename="output-cfg-images/1-nodes-highlighted.gv", format="pdf")
    s.view()

    all_nodes = cfg_nx.nodes
    all_edges = cfg_nx.edges

    cfg_nx_new = nx.MultiDiGraph()
    for node in all_nodes:
        cfg_nx_new.add_node(node)

    for edge in all_edges:
        cfg_nx_new.add_edge(edge[0], edge[1])

    cfg_dot_new = nx.nx_pydot.to_pydot(cfg_nx_new)

    s = Source(cfg_dot_new, filename="output-cfg-images/2-all-nodes.gv", format="pdf")
    s.view()

    # It will now merge the nodes
    nodes_to_be_added = {node: [node] for node in all_nodes if node not in nodes_to_be_removed}

    nodes_to_be_merged = nodes_to_be_removed
    nodes_to_be_merged.reverse()

    # Adds all the nodes whose predecessor is already part of the graph
    for node in nodes_to_be_merged:
        if cfg_nx.nodes[node] is not None:
            predecessor = [pred for pred in cfg_nx.nodes if node in cfg_nx[pred]][0]
            if predecessor in nodes_to_be_added:
                index_predecessor = nodes_to_be_added[predecessor].index(predecessor)
                nodes_to_be_added[predecessor].insert(index_predecessor + 1, node)
                nodes_to_be_removed.remove(node)

    # All the remaining nodes have a predecessor that was removed from the graph
    nodes_to_be_merged = nodes_to_be_removed
    while len(nodes_to_be_removed) > 0:
        for node in nodes_to_be_removed:
            predecessor = [pred for pred in cfg_nx.nodes if node in cfg_nx[pred]][0]
            for current_node in nodes_to_be_added:
                if predecessor in nodes_to_be_added[current_node]:
                    index_predecessor = nodes_to_be_added[current_node].index(predecessor)
                    nodes_to_be_added[current_node].insert(index_predecessor + 1, node)
                    nodes_to_be_merged.remove(node)

        nodes_to_be_removed = nodes_to_be_merged

    cfg_nx_merged = nx.MultiDiGraph()
    for node in nodes_to_be_added:
        cfg_nx_merged.add_node("-".join(nodes_to_be_added[node]))

    new_labels = {}
    for node in all_nodes:
        for new_node in nodes_to_be_added:
            if node in nodes_to_be_added[new_node]:
                new_labels[node] = "-".join(nodes_to_be_added[new_node])

    for edge in all_edges:
        if new_labels[edge[0]] != new_labels[edge[1]]:
            cfg_nx_merged.add_edge(new_labels[edge[0]], new_labels[edge[1]])

    cfg_dot_merged = nx.nx_pydot.to_pydot(cfg_nx_merged)

    s = Source(cfg_dot_merged, filename="output-cfg-images/3-merged-nodes.gv", format="pdf")
    s.view()


def main():
    cfg_filename = "6-cfg.dot"
    cfg_filepath = os.path.join(cfg_directory, cfg_filename)

    graphs = read_graph(cfg_filepath)
    if graphs is not None:
        cfg_dot = graphs[0]
        reduce_graph(cfg_dot)


if __name__ == "__main__":
    main()
