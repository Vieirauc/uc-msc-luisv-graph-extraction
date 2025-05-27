import os
import pandas as pd


from cfg_extraction_constants import CFG_FILE
from cfg_parsing import read_graph
from reduce_graph import reduce_graph, write_dot_file, write_statement_file

projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
data_directory = "output-data"
file_cfg_data_mask = "functions-{}-{}.csv"
graph = "cfg"

def generate_raw_cfg_artifacts(project):
    filepath = os.path.join("output-data", f"functions-cfg-{project}.csv")
    df = pd.read_csv(filepath, delimiter=";")
    df = df[df["CFG_filepath"].notnull()]

    for _, row in df.iterrows():
        cfg_filepath = row["CFG_filepath"]
        cfg_filepath_parts = cfg_filepath.split("\\")
        cfg_filename = cfg_filepath_parts[-1]
        cfg_name = cfg_filename.replace(".dot", "")

        if project != "httpd":
            repository_directory = cfg_filepath_parts[-2]
            output_commit_index = -3
            base_directory_max_index = -4
        else:
            repository_directory = ""
            output_commit_index = -2
            base_directory_max_index = -3

        output_commit = cfg_filepath_parts[output_commit_index]
        base_directory = "/".join(cfg_filepath_parts[:base_directory_max_index])

        graphs = read_graph(cfg_filepath, print_filepath=False)
        if graphs:
            cfg_dot = graphs[0]
            cfg_nx = nx.nx_pydot.from_pydot(cfg_dot)

            # Write as-is (not reduced)
            out_reduced_dir = os.path.join(base_directory, f"{project}-reduced", output_commit, repository_directory)
            out_statements_dir = os.path.join(base_directory, f"{project}-statements", output_commit, repository_directory)
            os.makedirs(out_reduced_dir, exist_ok=True)
            os.makedirs(out_statements_dir, exist_ok=True)

            write_dot_file(out_reduced_dir, cfg_name, cfg_nx)

            node_statements = {}
            for node in cfg_nx.nodes():
                node_name = str(node)
                dot_node = cfg_dot.get_node(f'"{node_name}"')
                if dot_node and dot_node[0].get_label():
                    node_statements[node_name] = [dot_node[0].get_label()]
                else:
                    # Still write the node, but with an empty list
                    node_statements[node_name] = []
            
            write_statement_file(out_statements_dir, cfg_name, node_statements)

def reduce_read_cfg_file(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(graph,project))
    df = pd.read_csv(filepath, delimiter=";")
    df = df[df[CFG_FILE].notnull()]

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]

        cfg_filepath_parts = cfg_filepath.split("\\")
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
                base_directory, "{}-reduced".format(project), output_commit, repository_directory)
            output_statements_directory = check_created_directory(
                base_directory, "{}-statements".format(project), output_commit, repository_directory)

            write_dot_file(output_reduced_directory, cfg_name, cfg_nx_merged)
            write_statement_file(output_statements_directory, cfg_name, node_statements)


def check_created_directory(base_directory, type_directory, output_commit, repository_directory):
    output_directory = os.path.join(base_directory, type_directory, output_commit, repository_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory


def main():
    for project in projects[3:4]:
        reduce_read_cfg_file(project)


if __name__ == "__main__":
    main()
