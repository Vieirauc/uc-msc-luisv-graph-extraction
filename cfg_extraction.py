import os
import subprocess


def extract_cfg(repository_path, commit):
    # sudo su -
    # cd /tmp
    # joern-parse /home/zema-21/Projects/httpd/  # ~ 1 minute
    # joern-export --repr cfg --out /tmp/output-cfg-3b365793c1 # ~15 seconds

    # Command to parse the source code
    parse_command = "joern-parse {}".format(repository_path)
    print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

    # Command to export the cfg
    graph_type = "cfg"
    # TODO: it needs some refactoring
    output_directory = "/tmp/output-{}-{}".format(graph_type, commit)
    parse_command = "joern-export --repr {} --out {}".format(graph_type, output_directory)
    print(subprocess.Popen(parse_command, shell=True, stdout=subprocess.PIPE).stdout.read())

    return output_directory
