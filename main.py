from cfg_extraction import extract_cfg
from cfg_parsing import map_cfg_per_function
from cfg_persistence import save_cfg
import os
from version_management import load_commit

target_commit = "3b365793c19aff95d1cf9bbea19f138752264d12"
commits = [target_commit]

base_project_directory = "/home/zema-21/Projects/"


def extract_cfg_per_commit(repository_path):
    for commit in commits:
        load_commit(commit)
        cfg_directory = extract_cfg(repository_path, commit)
        map_cfg_per_function(cfg_directory)
        save_cfg()


def main():
    project = "httpd"
    repository_path = os.path.join(base_project_directory, project)
    extract_cfg_per_commit(repository_path)


if __name__ == "__main__":
    main()
