from cfg_extraction import extract_cfg
from cfg_parsing import map_cfg_per_function
from cfg_persistence import save_cfg
from version_management import load_commit

target_commit = "3b365793c19aff95d1cf9bbea19f138752264d12"
commits = [target_commit]


def extract_cfg_per_commit():
    for commit in commits:
        load_commit(commit)
        extract_cfg()
        map_cfg_per_function()
        save_cfg()


def main():
    extract_cfg_per_commit()


if __name__ == "__main__":
    main()
