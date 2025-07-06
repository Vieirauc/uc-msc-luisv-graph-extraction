from cfg_extraction import extract_cfg, extract_cfg_per_file
from cfg_parsing import map_cfg_per_function
from cfg_persistence import save_cfg
import os
import pandas as pd
from version_management import load_commit
from convert_dot_to_json import map_functions_to_cfg
from reduce_cfg_batch import reduce_read_cfg_file, generate_unreduced_graph_artifacts
from cfg_feature_extraction import fex_read_cfg_file, fex_read_graph_file

target_commit = "3b365793c19aff95d1cf9bbea19f138752264d12"

base_project_directory = "C:/Users/luka3/Desktop/UC/MSI/Tese/code/projects"
commit_data_directory = "function-data"
commit_data_mask = "{}-functions.csv"
commit_data = "linux-functions.csv"
filepath = os.path.join(commit_data_directory, commit_data)
VULNERABLE_COMMIT_HASH = "Vulnerable Commit Hash"
FILE_PATH = "File Path"
SUBSET = True
GRAPH_TYPE = "ast"

base_output_directory = "C:/Users/luka3/Desktop/UC/MSI/Tese/code/uc-msc-luisv-graph_extractor/output"


def obtain_commits(project):
    # each file of "commit_data_directory" (function-data) is in the GitHub from João Henggeler
    # scripts/output/final/[PROJECT_NAME]/affected-files-[PROJECT_ID]-[PROJECT]-master-branch-[date].csv
    # e.g., "scripts/output/final/mozilla/affected-files-1-mozilla-master-branch-20210401212440.csv"
    filepath = os.path.join(commit_data_directory, commit_data_mask.format(project))
    df = pd.read_csv(filepath)
    commits = df[VULNERABLE_COMMIT_HASH].tolist()
    commits = list(set(commits))
    return commits


def obtain_commits_files(project):
    # each file of "commit_data_directory" (function-data) is in the GitHub from João Henggeler
    # scripts/output/final/[PROJECT_NAME]/affected-files-[PROJECT_ID]-[PROJECT]-master-branch-[date].csv
    # e.g., "scripts/output/final/mozilla/affected-files-1-mozilla-master-branch-20210401212440.csv"
    #filepath = os.path.join(commit_data_directory, commit_data_mask.format(project))
    filepath = os.path.join(commit_data_directory, commit_data)
    df = pd.read_csv(filepath)
    commits = df[VULNERABLE_COMMIT_HASH].tolist()
    commits = list(set(commits))
    commits_files = {}
    for commit in commits:
        commits_files[commit] = df[df[VULNERABLE_COMMIT_HASH] == commit][FILE_PATH].tolist()
    print(f"Obtained {len(commits_files)} commits with files for project {project}.")
    #print commits_ffiles dictionary
    #for commit, files in commits_files.items():
        #print(f"Commit: {commit}, Files: {len(files)}")
    return commits_files


def check_output_directory(base_output_directory, project):
    output_directory = os.path.join(base_output_directory, project)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)


def should_run_per_directory(project):
    return project in ["glibc", "gecko-dev", "linux"]


def extract_cfg_per_commit(project, commits):
    repository_path = os.path.join(base_project_directory, project)
    check_output_directory(base_output_directory, project)
    for commit in commits:
        load_commit(repository_path, commit)
        cfg_directory = extract_cfg(base_output_directory, project,
                                    repository_path, commit, should_run_per_directory(project))
        map_cfg_per_function(cfg_directory)
        save_cfg()


def extract_cfg_per_commit_file(project, commits_files, graph_type_list=["cfg"]):
    repository_path = os.path.join(base_project_directory, project)
    check_output_directory(base_output_directory, project)
    
    for commit in commits_files:
        skip_commit = True

        for graph_type in graph_type_list:
            output_directory = os.path.join(base_output_directory, project,
                                            f"output-{graph_type}-{commit}")
            if not os.path.exists(output_directory):
                skip_commit = False
                break  # If at least one graph_type is missing, we need to process this commit

        if skip_commit:
            print(f"[SKIP] All graph types already extracted for commit {commit}.")
            continue

        # Checkout to the commit
        load_commit(repository_path, commit)

        # Extract graph types
        for graph_type in graph_type_list:
            cfg_directory = extract_cfg_per_file(base_output_directory, project,
                                                 repository_path, commit, 
                                                 commits_files[commit], graph_type)
            #map_cfg_per_function(cfg_directory)
            #save_cfg()

def summarize_extraction_status(project, graph_type_list):
    import pandas as pd

    filepath = os.path.join(commit_data_directory, commit_data)
    df = pd.read_csv(filepath)

    # Commit hashes únicos da coluna "Vulnerable Commit Hash"
    unique_commits = set(df[VULNERABLE_COMMIT_HASH].dropna().unique())
    print(f"\n[INFO] Total unique commits in dataset: {len(unique_commits)}")

    project_output_path = os.path.join(base_output_directory, project)
    results = {}

    for graph_type in graph_type_list:
        # Procurar diretórios do tipo output-ast-* ou output-pdg-* etc
        extracted_commits = {
            folder.split(f"output-{graph_type}-")[-1]
            for folder in os.listdir(project_output_path)
            if folder.startswith(f"output-{graph_type}-")
        }

        missing_commits = unique_commits - extracted_commits

        print(f"\n[{graph_type.upper()}]")
        print(f"✓ Extracted: {len(extracted_commits)}")
        print(f"✗ Missing:   {len(missing_commits)}")

        results[graph_type] = {
            "extracted": len(extracted_commits),
            "missing": len(missing_commits),
            "done_commits": list(extracted_commits),
            "missing_commits": list(missing_commits),
        }

    return results


def main():
    projects = ["httpd", "glibc", "gecko-dev", "linux", "xen"]
    graph_type_list = ["ast", "pdg"]
    for project in ["linux"]:
        summarize_extraction_status(project, graph_type_list)
        commits_files = obtain_commits_files(project)
        extract_cfg_per_commit_file(project, commits_files,graph_type_list)
        for graph_type in graph_type_list:
            print(f"\n### Processing {project} - {graph_type} ###")
            # Extract the CFG for the listed files only
            
             # calls extract_cfg_per_file from cfg_extraction.py
            map_functions_to_cfg(project,graph_type,csv_filename=filepath)                     # from convert_dot_to_json.py
            generate_unreduced_graph_artifacts(project,graph_type)                     # from reduce_cfg_batch.py (skips the reduction)
            #reduce_read_cfg_file(project,graph_type)                              # from reduce_cfg_batch.py
            fex_read_graph_file(project,graph_type)                              # from cfg_feature_extraction.py
            


if __name__ == "__main__":
    main()
