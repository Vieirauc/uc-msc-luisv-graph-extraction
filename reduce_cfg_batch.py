import os
import pandas as pd

from cfg_extraction_constants import CFG_FILE

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


def main():
    for project in projects[2:3]:
        read_cfg_file(project)


if __name__ == "__main__":
    main()
