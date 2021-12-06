from cfg_extraction_constants import CFG_FILE
from cfg_parsing import read_graph
import os
import pandas as pd

projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}.csv"


def analyze_double_edge(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)
    df = df[df[CFG_FILE].notnull()]

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]

        cfg_filepath_parts = cfg_filepath.split("/")
        cfg_filename = cfg_filepath_parts[-1]
        repository_directory = cfg_filepath_parts[-2]
        output_commit = cfg_filepath_parts[-3]
        base_directory = "/".join(cfg_filepath_parts[0:-4])

        reduced_cfg_path = os.path.join(
            base_directory, "{}-reduced".format(project), output_commit, repository_directory, cfg_filename)
        print(reduced_cfg_path)

        graphs = read_graph(reduced_cfg_path)

        if graphs is not None:
            cfg_dot = graphs[0]


def main():
    for project in projects[2:3]:
        analyze_double_edge(project)


if __name__ == "__main__":
    main()