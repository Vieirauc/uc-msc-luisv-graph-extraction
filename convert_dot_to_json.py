# dot_to_json_graph.py
# http://stackoverflow.com/questions/40262441/how-to-transform-a-dot-graph-to-json-graph

# Packages needed  :
# sudo aptitude install python-networkx python-pygraphviz python-pydot
#
# Syntax :
# python dot_to_json_graph.py graph.dot

from cfg_parsing import adjust_file, get_graph_name
import networkx as nx
from networkx.readwrite import json_graph
import json
import os
import pandas as pd
from tqdm import tqdm

base_dot_directory = "output"
commit_data_directory = "function-data"
output_directory = "output-data"
projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
commit_data_mask = "{}-functions.csv"
commit_data="selected_code_units.csv"
filepath = os.path.join(commit_data_directory, commit_data)
VULNERABLE_COMMIT_HASH = "Vulnerable Commit Hash"
FILE_PATH = "File Path"
VULNERABLE_FUNCTIONS = "Vulnerable File Functions"

def convert_dot_to_json(project):
    project_dir = os.path.join(base_dot_directory, project)
    wrong_files = []
    for directory in os.listdir(project_dir)[0:1]:
        print(directory)
        files = os.listdir(os.path.join(project_dir, directory))
        for filename in files:
            try:
                dot_filepath = os.path.join(project_dir, directory, filename)
                adjust_file(dot_filepath)
                dot_graph = nx.nx_pydot.read_dot(dot_filepath)
                print(json.dumps(json_graph.node_link_data(dot_graph)))
            except TypeError:
                wrong_files.append(dot_filepath)
    print("Files with problems ({}): {} ".format(len(wrong_files), wrong_files))


def directory_per_file(project):
    return project in ["glibc", "gecko-dev", "linux"]


def write_output_file_append(output_filename, row):
    header = 'commit;filepath;function_name;CFG_filepath;vulnerable_label\n'
    output_filepath = os.path.join(output_directory, output_filename)
    
    if not os.path.exists(output_filepath):
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        with open(output_filepath, 'w') as output_file:
            output_file.write(header)
    
    with open(output_filepath, 'a') as output_file:
        output_file.write(row)

def map_functions_to_graph(project, graph_type="ast", csv_filename=None):
    import re

    filepath = os.path.join(commit_data_directory, commit_data_mask.format(project))

    output_name = f"functions-{graph_type}-{project}.csv"
    output_path = os.path.join(output_directory, output_name)

    # ✅ Carregar funções já processadas
    processed_keys = set()
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            next(f)
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 3:
                    processed_keys.add((parts[0], parts[1], parts[2]))

    # ✅ Filtrar apenas commits que ainda têm funções por processar
    def has_unprocessed_functions(row):
        try:
            functions = json.loads(row[VULNERABLE_FUNCTIONS])
        except Exception:
            return False
        for f in functions:
            key = (row[VULNERABLE_COMMIT_HASH], row[FILE_PATH], f["Name"])
            if key not in processed_keys:
                return True
        return False

    df = pd.read_csv(filepath)
    df = df[df[VULNERABLE_FUNCTIONS].notnull()]
    df = df[df.apply(has_unprocessed_functions, axis=1)]

    print(f"[INFO] Mapping functions to {graph_type.upper()} graphs for project: {project}")
    print(f"[INFO] {len(processed_keys)} functions already processed (checkpointing enabled)")
    print(f"[INFO] {len(df)} commits/files need processing")

    processed_count = 0
    for i, (_, row) in enumerate(df.iterrows(), 1):
        commit = row[VULNERABLE_COMMIT_HASH]
        file_path = row[FILE_PATH]

        cfg_output_directory = os.path.join(base_dot_directory, project, f"output-{graph_type}-{commit}")
        if directory_per_file(project):
            filepath_directory = file_path.replace("/", "---")
            cfg_output_directory = os.path.join(cfg_output_directory, filepath_directory)

        try:
            cfg_files = os.listdir(cfg_output_directory)
        except FileNotFoundError:
            print(f"[WARN] Missing graph directory: {cfg_output_directory}")
            continue

        map_function_name_cfgfile = {
            get_graph_name(cfg_output_directory, cfg_file): os.path.join(cfg_output_directory, cfg_file)
            for cfg_file in cfg_files
        }

        try:
            functions = json.loads(row[VULNERABLE_FUNCTIONS])
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse functions in {file_path}@{commit}")
            continue

        for function in functions:
            function_name = function["Name"]
            key = (commit, file_path, function_name)

            if key in processed_keys:
                continue

            vulnerable = function["Vulnerable"] == "Yes"
            cfg_filepath = map_function_name_cfgfile.get(function_name, "")

            if not cfg_filepath:
                scoped_matches = [k for k in map_function_name_cfgfile if f"::{function_name}" in k]
                if scoped_matches:
                    cfg_filepath = map_function_name_cfgfile[scoped_matches[0]]
                else:
                    print(f"[WARN] Não encontrou função: {function_name} em {file_path}@{commit}")
                    cfg_filepath = ""

            csv_row = f"{commit};{file_path};{function_name};{cfg_filepath};{vulnerable}\n"
            write_output_file_append(output_name, csv_row)

        processed_count += 1
        if processed_count % 50 == 0:
            print(f"[INFO] {processed_count}/{len(df)} commits/files processed...")

    print(f"[DONE] Finished mapping functions to {graph_type.upper()} for {project}")


def main():
    for project in projects[3:4]:
        #if directory_per_file(project):
        #    map_functions_to_cfg(project)
        #else:
        #    convert_dot_to_json(project)
        map_functions_to_cfg(project)


if __name__ == "__main__":
    main()
