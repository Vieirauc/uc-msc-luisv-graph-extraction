import json
import os
import pandas as pd

data_directory = "function-data"
VULNERABLE_FUNCTIONS_HEADER = "Vulnerable File Functions"


def load_commit(commit):
    print("load_commit to be implemented")
    return
    for filename in os.listdir(data_directory):
        filepath = os.path.join(data_directory, filename)

        df = pd.read_csv(filepath)
        df = df[df["Vulnerable Commit Hash"] == commit]
        df = df[df[VULNERABLE_FUNCTIONS_HEADER].notna()]
        print(df.columns)
        print(df.shape)
        print(df[VULNERABLE_FUNCTIONS_HEADER])

        for index, row in df.iterrows():
            print(row["File Path"])
            functions = json.loads(row[VULNERABLE_FUNCTIONS_HEADER])
            #print(functions)
            for function in functions:
                #print(row["File Path"], function["Name"], function["Vulnerable"])
                function_name = function["Name"]

