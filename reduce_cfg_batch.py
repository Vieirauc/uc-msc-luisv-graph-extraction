import os
import pandas as pd
import networkx as nx
import html
from networkx.drawing.nx_pydot import from_pydot


from cfg_extraction_constants import CFG_FILE
from cfg_parsing import read_graph
from reduce_graph import reduce_graph, write_dot_file, write_statement_file

projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
data_directory = "output-data"
file_cfg_data_mask = "functions-{}-{}.csv"
graph = "ast"

from tqdm import tqdm

def generate_unreduced_graph_artifacts(project, graph_type):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(graph_type, project))
    df = pd.read_csv(filepath, delimiter=";")
    df = df[df[CFG_FILE].notnull()]

    already_processed = 0
    processed_now = 0
    total = len(df)

    print(f"[INFO] Starting graph artifact generation for {project.upper()} ({graph_type.upper()})")
    print(f"[INFO] Total graphs in dataset: {total}")

    for index, row in df.iterrows():
        graph_filepath = row[CFG_FILE]

        graph_filepath_parts = graph_filepath.split("\\" if "\\" in graph_filepath else "/")
        graph_filename = graph_filepath_parts[-1]
        graph_name = graph_filename.replace(".dot", "")

        if project != "httpd":
            repository_directory = graph_filepath_parts[-2]
            output_commit_index = -3
            base_directory_max_index = -4
        else:
            repository_directory = ""
            output_commit_index = -2
            base_directory_max_index = -3

        output_commit = graph_filepath_parts[output_commit_index]
        base_directory = "/".join(graph_filepath_parts[:base_directory_max_index])

        output_reduced_directory = check_created_directory(
            base_directory, f"{project}-{graph_type}-reduced", output_commit, repository_directory)
        output_statements_directory = check_created_directory(
            base_directory, f"{project}-{graph_type}-statements", output_commit, repository_directory)

        output_reduced_path = os.path.join(output_reduced_directory, f"{graph_name}.dot")
        output_statements_path = os.path.join(output_statements_directory, f"{graph_name}.txt")

        # ✅ Skip already processed
        if os.path.exists(output_reduced_path) and os.path.exists(output_statements_path):
            already_processed += 1
            continue

        try:
            graphs = read_graph(graph_filepath)
            if graphs is None:
                print(f"[WARN] Could not read graph file: {graph_filepath}")
                continue
        except Exception as e:
            print(f"[ERROR] Failed to parse graph file: {graph_filepath} | {e}")
            continue

        graph_dot = graphs[0]
        graph_nx = nx.nx_pydot.from_pydot(graph_dot)

        write_dot_file(output_reduced_directory, graph_name, graph_nx)

        node_statements = {}
        for node in graph_nx.nodes():
            try:
                dot_node = graph_dot.get_node(f'"{node}"')
                if dot_node and dot_node[0].get_label():
                    label = dot_node[0].get_label()
                    node_statements[str(node)] = [label]
                else:
                    node_statements[str(node)] = []
            except Exception as e:
                print(f"[WARN] Failed to get label for node {node}: {e}")
                node_statements[str(node)] = []

        write_statement_file(output_statements_directory, graph_name, node_statements)

        processed_now += 1
        if processed_now % 50 == 0:
            print(f"[INFO] Processed {processed_now} new graphs... ({already_processed} were already done)")

    print(f"[DONE] Finished graph artifact generation for {project.upper()} ({graph_type.upper()})")
    print(f"[INFO] Skipped {already_processed} already processed graphs")
    print(f"[INFO] Newly processed: {processed_now}")



def reduce_read_cfg_file(project,graph_type="cfg"):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project,graph_type))
    df = pd.read_csv(filepath, delimiter=";")
    df = df[df[CFG_FILE].notnull()]

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]

        cfg_filepath_parts = cfg_filepath.split("\\" if "\\" in cfg_filepath else "/")
        cfg_filename = cfg_filepath_parts[-1]
        cfg_name = cfg_filename[:cfg_filename.index(".dot")]

        if project != "httpd":
            repository_directory = cfg_filepath_parts[-2]
            output_commit_index = -3
            base_directory_max_index = -4
        else:
            repository_directory = ""
            output_commit_index = -2
            base_directory_max_index = -3
        output_commit = cfg_filepath_parts[output_commit_index]
        base_directory = "/".join(cfg_filepath_parts[0:base_directory_max_index])

        graphs = read_graph(cfg_filepath)

        if graphs is not None:
            cfg_dot = graphs[0]
            cfg_nx_merged, node_statements = reduce_graph(cfg_dot)

            output_reduced_directory = check_created_directory(
                base_directory, "{}-{}-reduced".format(project,graph_type), output_commit, repository_directory)
            output_statements_directory = check_created_directory(
                base_directory, "{}-{}-statements".format(project,graph_type), output_commit, repository_directory)

            write_dot_file(output_reduced_directory, cfg_name, cfg_nx_merged)
            write_statement_file(output_statements_directory, cfg_name, node_statements)


def check_created_directory(base_directory, type_directory, output_commit, repository_directory):
    output_directory = os.path.join(base_directory, type_directory, output_commit, repository_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory


def main():
    for project in projects[3:4]:
        generate_unreduced_graph_artifacts(project,"ast") 


if __name__ == "__main__":
    main()
