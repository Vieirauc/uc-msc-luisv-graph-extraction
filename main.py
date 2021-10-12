from cfg_extraction import extract_cfg
from cfg_parsing import map_cfg_per_function
from cfg_persistence import save_cfg
import os
import pandas as pd
from version_management import load_commit

target_commit = "3b365793c19aff95d1cf9bbea19f138752264d12"

base_project_directory = "/home/zema-21/Projects/"
commit_data_directory = "function-data"
commit_data_mask = "{}-functions.csv"
VULNERABLE_COMMIT_HASH = "Vulnerable Commit Hash"

base_output_directory = "/opt/josep"


def obtain_commits(project):
    filepath = os.path.join(commit_data_directory, commit_data_mask.format(project))
    df = pd.read_csv(filepath)
    commits = df[VULNERABLE_COMMIT_HASH].tolist()
    commits = list(set(commits))
    return commits


def extract_cfg_per_commit(project, commits):
    repository_path = os.path.join(base_project_directory, project)
    for commit in commits:
        load_commit(repository_path, commit)
        cfg_directory = extract_cfg(base_output_directory, project,
                                    repository_path, commit)
        map_cfg_per_function(cfg_directory)
        save_cfg()


def main():
    projects = ["httpd"]
    for project in projects:
        commits = obtain_commits(project)
        extract_cfg_per_commit(project, commits)


if __name__ == "__main__":
    main()
