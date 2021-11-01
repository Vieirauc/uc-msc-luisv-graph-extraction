import os
import subprocess


def obtain_directories(repository_path, run_per_directory):
    if run_per_directory:
        return [os.path.join(repository_path, directory)
                for directory in os.listdir(repository_path)
                if os.path.isdir(os.path.join(repository_path, directory)) and
                not directory.startswith(".")]
    return [repository_path]


def extract_cfg(base_output_directory, project, repository_path, commit, run_per_directory=False):
    # joern-parse [repository_path]
    # joern-export --repr cfg --out [output_directory]

    graph_type = "cfg"
    output_directory = os.path.join(base_output_directory, project,
                                    "output-{}-{}".format(graph_type, commit))

    # If the directory exists, the parsing was already performed for that commit
    if not os.path.exists(output_directory):
        # Command to parse the source code
        for directory in obtain_directories(repository_path, run_per_directory):
            parse_command = "joern-parse {}".format(directory)
            print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

        # Command to export the cfg
        # TODO still not sure if this should be done per directory
        parse_command = "joern-export --repr {} --out {}".format(graph_type, output_directory)
        print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

    return output_directory
