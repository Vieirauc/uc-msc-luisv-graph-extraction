from cfg_parsing import read_graph
import os
import pandas as pd


data_directory = "output-data"
file_cfg_data_mask = "functions-cfg-{}-sample.csv"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
CFG_FILE = "CFG_filepath"


def read_cfg_file(project):
    filepath = os.path.join(data_directory, file_cfg_data_mask.format(project))
    df = pd.read_csv(filepath)

    for index, row in df.iterrows():
        cfg_filepath = row[CFG_FILE]
        print(cfg_filepath)
        graphs = read_graph(cfg_filepath)

        if graphs is not None:
            print(graphs[0])


def main():
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
