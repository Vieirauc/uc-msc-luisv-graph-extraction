import pandas as pd
import re

# File paths
cfg_dataset_path = "C:/Users/luka3/Desktop/UC/MSI/Tese/code/cfg-extractor/subsets/cfg-dataset-linux-v0.5.csv"
linux_functions_path = "C:/Users/luka3/Desktop/UC/MSI/Tese/code/cfg-extractor/subsets/linux-functions.csv"

# Load datasets
cfg_dataset_df = pd.read_csv(cfg_dataset_path, delimiter=";")
linux_functions_df = pd.read_csv(linux_functions_path)

# Extract commit hashes and file paths from CFG dataset
def extract_commit_and_filepath(cfg_path):
    match = re.search(r'output-cfg-([a-f0-9]+)/(.+?)/\d+-cfg\.dot$', str(cfg_path))
    if match:
        return match.group(1), match.group(2).replace('---', '/')
    return None, None

cfg_dataset_df["Commit Hash"], cfg_dataset_df["Linux File Path"] = zip(
    *cfg_dataset_df["cfg_filepath"].apply(extract_commit_and_filepath)
)

# Function to filter functions based on user selection
def select_code_units(vulnerable=True, cfg_size=1, num_samples=10):
    """
    Selects a specified number of vulnerable or non-vulnerable functions
    that generate CFGs of the given size.
    
    :param vulnerable: Boolean - True for vulnerable functions, False for non-vulnerable.
    :param cfg_size: int - Size of the CFG (1 for single-node, >1 for multi-node).
    :param num_samples: int - Number of functions to retrieve.
    :return: DataFrame - Filtered functions in the same format as linux-functions.csv.
    """

    # Filter CFG dataset by size
    if cfg_size == 1:
        cfg_filtered = cfg_dataset_df[cfg_dataset_df["size"] == 1]
    else:
        cfg_filtered = cfg_dataset_df[cfg_dataset_df["size"] > 1]

    # Filter Linux functions dataset to only include entries that match the CFG dataset
    filtered_functions = linux_functions_df[
        (linux_functions_df["File Path"].isin(cfg_filtered["Linux File Path"])) &
        (linux_functions_df["Vulnerable Commit Hash"].isin(cfg_filtered["Commit Hash"]))
    ]

    # Select vulnerable or non-vulnerable functions
    if vulnerable:
        selected_functions = filtered_functions[filtered_functions["Vulnerable File Functions"].notna()]
    else:
        selected_functions = filtered_functions[filtered_functions["Vulnerable File Functions"].isna()]

    # Sample the requested number of functions
    selected_subset = selected_functions.sample(n=min(num_samples, len(selected_functions)), random_state=42)

    return selected_subset

# Example usage: Retrieve 5 vulnerable functions with CFG size 1
selected_data = select_code_units(vulnerable=True, cfg_size=1, num_samples=5)

# Save to CSV in the same format as linux-functions.csv
output_path = "selected_code_units.csv"
selected_data.to_csv(output_path, index=False)

print(f"Saved selected code units to {output_path}")
