import pandas as pd
import re
import csv
import json
import ast
import sys
import os
import random

def count_functions_per_program(csv_file_path):
    """
    Counts the number of functions per program (per row) in the 'Vulnerable File Functions'
    column of the given CSV file.
    
    Parameters:
        csv_file_path (str): Path to the CSV file.
    
    Returns:
        dict: Dictionary mapping the 'File Path' to the number of functions in that row.
    """
    functions_per_program = {}

    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            file_path = row['File Path']
            functions_list_str = row['Vulnerable File Functions']
            
            try:
                functions_list = json.loads(functions_list_str)
            except json.JSONDecodeError:
                # Skip rows that can't be parsed
                continue
            
            # Number of functions for this program
            functions_per_program[file_path] = len(functions_list)

    return functions_per_program

def check_memory_features_in_graphs(csv_path):
    graphs_with_mm_features = []

    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Skip header

        for row in reader:
            if len(row) != 5:
                continue  # skip malformed rows

            cfg_path, label, size, adj_matrix_str, feat_matrix_str = row
            size = int(size)
            feature_matrix_flat = ast.literal_eval(feat_matrix_str)

            if len(feature_matrix_flat) != size * 19:
                print(f"[WARN] Feature matrix size mismatch in {cfg_path}")
                continue

            found_mm = False
            for i in range(size):
                node_features = feature_matrix_flat[i * 19:(i + 1) * 19]
                mm_features = node_features[-8:]
                if any(f > 0 for f in mm_features):
                    found_mm = True
                    break

            if found_mm:
                graphs_with_mm_features.append(cfg_path)

    return graphs_with_mm_features

def get_largest_graph_info(csv_path):
    max_size = -1
    max_cfg_path = None
    max_line_number = -1

    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # skip header

        for line_number, row in enumerate(reader, start=2):  # start=2 to account for header
            if len(row) < 3:
                continue
            try:
                size = int(row[2])
                if size > max_size:
                    max_size = size
                    max_cfg_path = row[0]
                    max_line_number = line_number
            except ValueError:
                continue

    print(f"Grafo com maior size:")
    print(f"  Filepath: {max_cfg_path}")
    print(f"  Size: {max_size}")
    print(f"  Linha no CSV: {max_line_number}")
    return max_cfg_path, max_size, max_line_number

import pandas as pd

import pandas as pd
import numpy as np

def describe_large_dataset(input_path, chunksize=5000):
    total, num_vuln, num_safe = 0, 0, 0
    min_size, max_size = float('inf'), 0
    max_size_filepath = None
    all_sizes = []

    print(f"Lendo estatísticas do dataset: {input_path}")

    for chunk in pd.read_csv(input_path, sep=';', chunksize=chunksize):
        chunk['label'] = chunk['label'].astype(bool)

        total += len(chunk)
        num_vuln += chunk['label'].sum()
        num_safe += len(chunk) - chunk['label'].sum()

        # Acumula tamanhos para média e percentil
        all_sizes.extend(chunk['size'].tolist())

        chunk_max_size = chunk['size'].max()
        chunk_min_size = chunk['size'].min()

        if chunk_max_size > max_size:
            max_size = chunk_max_size
            max_size_filepath = chunk.loc[chunk['size'].idxmax(), 'cfg_filepath']

        min_size = min(min_size, chunk_min_size)

        print(f"🔄 Acumulado: {total} linhas...")

    prop_vuln = num_vuln / total if total > 0 else 0
    mean_size = np.mean(all_sizes)
    p95_size = np.percentile(all_sizes, 95)

    print("\nEstatísticas finais:")
    print(f"Total de funções: {total}")
    print(f"Funções vulneráveis: {num_vuln}")
    print(f"Funções não vulneráveis: {num_safe}")
    print(f"Proporção vulneráveis: {prop_vuln:.2%}")
    print(f"Tamanho mínimo do grafo: {min_size}")
    print(f"Tamanho máximo do grafo: {max_size}")
    print(f"Arquivo correspondente ao maior grafo: {max_size_filepath}")
    print(f"Tamanho médio dos grafos: {mean_size:.2f}")
    print(f"95º percentil do tamanho dos grafos: {p95_size:.2f}")

    return {
        'total': total,
        'num_vuln': num_vuln,
        'num_safe': num_safe,
        'prop_vuln': prop_vuln,
        'min_size': min_size,
        'max_size': max_size,
        'max_size_filepath': max_size_filepath,
        'mean_size': mean_size,
        'p95_size': p95_size
    }

import random

def undersample_preserve_ratio(input_path, output_path, max_total=10000):
    """
    Memory-efficient undersampling that preserves original class ratio.
    """
    vuln_total = 0
    nonvuln_total = 0

    # First pass: count totals
    print(" Calculando proporção original...")
    with open(input_path, "r") as f:
        header = f.readline()
        label_idx = header.strip().split(";").index("label")

        for line in f:
            if not line.strip():
                continue
            label = line.strip().split(";")[label_idx].strip().lower()
            if label in ["1", "true", "yes"]:
                vuln_total += 1
            else:
                nonvuln_total += 1

    total_entries = vuln_total + nonvuln_total
    vuln_ratio = vuln_total / total_entries
    nonvuln_ratio = 1 - vuln_ratio

    vuln_keep = int(max_total * vuln_ratio)
    nonvuln_keep = max_total - vuln_keep

    print(f" Proporção original: {vuln_ratio:.4f} vulneráveis")
    print(f" Alvo: {vuln_keep} vulneráveis + {nonvuln_keep} não-vulneráveis")

    # Second pass: reservoir sampling
    reservoir_vuln = []
    reservoir_nonvuln = []
    seen_vuln = 0
    seen_nonvuln = 0

    with open(input_path, "r") as f:
        header = f.readline()  # again
        for line_num, line in enumerate(f):
            if not line.strip():
                continue
            label = line.strip().split(";")[label_idx].strip().lower()
            if label in ["1", "true", "yes"]:
                seen_vuln += 1
                if len(reservoir_vuln) < vuln_keep:
                    reservoir_vuln.append(line)
                else:
                    r = random.randint(0, seen_vuln)
                    if r < vuln_keep:
                        reservoir_vuln[r] = line
            else:
                seen_nonvuln += 1
                if len(reservoir_nonvuln) < nonvuln_keep:
                    reservoir_nonvuln.append(line)
                else:
                    r = random.randint(0, seen_nonvuln)
                    if r < nonvuln_keep:
                        reservoir_nonvuln[r] = line

            if line_num % 100000 == 0 and line_num > 0:
                print(f" Processadas {line_num:,} linhas...")

    print(f"\n Visto: {seen_vuln} vulneráveis, {seen_nonvuln} não-vulneráveis")
    print(f" Selecionado: {len(reservoir_vuln)} + {len(reservoir_nonvuln)}")

    with open(output_path, "w") as fout:
        fout.write(header)
        for line in reservoir_vuln + reservoir_nonvuln:
            fout.write(line)

    print(f"\n Dataset final com proporção preservada salvo em: {output_path}")


def main():
    #input_dataset = "/home/lucaspc/tese/uc-msc-luisv-graph_extractor/output/cfg-dataset-linux-v0.5_filtered.csv"
    #input_dataset = "/home/lucaspc/tese/uc-msc-luisv-graph_extractor/output/cfg-dataset-linux-v0.5_filtered_undersampled10k.csv"
    input_dataset = "/home/lucaspc/tese/uc-msc-luisv-graph_extractor/output/pdg-dataset-linux.csv"
    output_dataset = input_dataset.replace(".csv", "_undersampled20k.csv")

    describe_large_dataset(output_dataset, chunksize=5000)
    #undersample_preserve_ratio(input_dataset, output_dataset, max_total=20000)
    #describe_large_dataset(output_dataset, chunksize=5000)

    #describe
    #undersample_adaptive_chunked(input_dataset,output_dataset,max_total=10000,min_vuln_ratio=0.2)
    

if __name__ == "__main__":
    main()
