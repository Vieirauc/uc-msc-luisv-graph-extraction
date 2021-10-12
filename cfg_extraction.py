import os
import subprocess


def extract_cfg(base_output_directory, project, repository_path, commit):
    # joern-parse [repository_path]
    # joern-export --repr cfg --out [output_directory]

    # Command to parse the source code
    parse_command = "joern-parse {}".format(repository_path)
    print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

    graph_type = "cfg"
    output_directory = os.path.join(base_output_directory, project,
                                    "output-{}-{}".format(graph_type, commit))

    # Command to export the cfg
    parse_command = "joern-export --repr {} --out {}".format(graph_type, output_directory)
    print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

    return output_directory
