import os
import pandas as pd

from cfg_extraction_constants import CFG_FILE
from cfg_parsing import read_graph
from reduce_graph import reduce_graph, write_dot_file, write_statement_file

# It should run the CFG reduction and save a summary file with the following fields
# commit,filepath,function_name,reduced_CFG_filepath,STATEMENTS_FILE,vulnerable_label

# Some of the fields names are defined in the constant files

projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}.csv"


def read_cfg_file(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)
    df = df[df[CFG_FILE].notnull()]

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]
        print(cfg_filepath)

        cfg_filepath_parts = cfg_filepath.split("/")
        cfg_filename = cfg_filepath_parts[-1]
        cfg_name = cfg_filename[:cfg_filename.index(".dot")]
        repository_directory = cfg_filepath_parts[-2]
        output_commit = cfg_filepath_parts[-3]
        base_directory = "/".join(cfg_filepath_parts[0:-4])

        graphs = read_graph(cfg_filepath)

        if graphs is not None:
            cfg_dot = graphs[0]
            cfg_nx_merged, node_statements = reduce_graph(cfg_dot, True)

            output_reduced_directory = check_created_directory(
                base_directory, "{}-reduced", output_commit, repository_directory)
            output_statements_directory = check_created_directory(
                base_directory, "{}-statements", output_commit, repository_directory)

            write_dot_file(output_reduced_directory, cfg_name, cfg_nx_merged)
            write_statement_file(output_statements_directory, cfg_name, node_statements)

        if index == 10:
            return


def check_created_directory(base_directory, type_directory, output_commit, repository_directory):
    output_directory = os.path.join(base_directory, type_directory, output_commit, repository_directory)
    if not os.path.exists:
        os.makedirs(output_directory)
    return output_directory


def main():
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
