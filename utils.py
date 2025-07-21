import pandas as pd
import re
import csv
import json
import ast
import sys
import os



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

    print(f"📊 Lendo estatísticas do dataset: {input_path}")

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

    print("\n📈 Estatísticas finais:")
    print(f"Total de funções: {total}")
    print(f"Funções vulneráveis: {num_vuln}")
    print(f"Funções não vulneráveis: {num_safe}")
    print(f"Proporção vulneráveis: {prop_vuln:.2%}")
    print(f"Tamanho mínimo do grafo: {min_size}")
    print(f"Tamanho máximo do grafo: {max_size}")
    print(f" ↪️ Arquivo correspondente ao maior grafo: {max_size_filepath}")
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


import os
import random

def undersample_adaptive_chunked(input_path, output_path, max_total=10000, min_vuln_ratio=0.3):
    vuln_count = 0
    non_vuln_temp = output_path.replace(".csv", "_nonvuln_temp.csv")
    print(f"\n🔍 Iniciando undersampling (sem pandas, só I/O)...")

    with open(input_path, "r") as fin, \
         open(output_path, "w") as fout_vuln, \
         open(non_vuln_temp, "w") as fout_nonvuln:

        header = fin.readline()
        fout_vuln.write(header)
        fout_nonvuln.write(header)

        label_idx = header.strip().split(";").index("label")

        for i, line in enumerate(fin):
            if not line.strip():
                continue

            parts = line.strip().split(";")
            label = parts[label_idx].strip().lower()

            if label in ["1", "true", "yes"]:
                fout_vuln.write(line)
                vuln_count += 1
            else:
                fout_nonvuln.write(line)

            if i % 100000 == 0:
                print(f"🔄 Processadas {i} linhas...")

    print(f"✅ Vulneráveis encontrados: {vuln_count}")

    # Etapa 2: decidir limites
    if vuln_count >= max_total:
        vuln_keep = int(max_total * min_vuln_ratio)
        nonvuln_needed = max_total - vuln_keep
        skip_vuln = vuln_count - vuln_keep
        print(f"⚠️ Usando ratio mínima de {min_vuln_ratio*100:.1f}%. Mantendo {vuln_keep} vulneráveis")
    else:
        vuln_keep = vuln_count
        nonvuln_needed = max_total - vuln_keep
        skip_vuln = 0
        print(f"✂️ Mantendo todos os {vuln_keep} vulneráveis")

    # Etapa 3: reescrever apenas N vulneráveis
    with open(output_path, "r") as vin, open(output_path + ".tmp", "w") as vout:
        vout.write(vin.readline())  # header
        kept = 0
        for line in vin:
            if skip_vuln > 0:
                skip_vuln -= 1
                continue
            if kept >= vuln_keep:
                break
            vout.write(line)
            kept += 1
    os.replace(output_path + ".tmp", output_path)

    # Etapa 4: sample de não vulneráveis por reservoir
    print(f"📦 Amostrando {nonvuln_needed} não vulneráveis (modo streaming)")
    reservoir = []
    line_count = 0
    with open(non_vuln_temp, "r") as f:
        _ = f.readline()  # skip header
        for line in f:
            line_count += 1
            if len(reservoir) < nonvuln_needed:
                reservoir.append(line)
            else:
                r = random.randint(0, line_count)
                if r < nonvuln_needed:
                    reservoir[r] = line

    with open(output_path, "a") as fout:
        for line in reservoir:
            fout.write(line)

    os.remove(non_vuln_temp)
    print(f"\n🎯 Dataset final salvo em: {output_path}")
    print(f"Estimado: {vuln_keep + nonvuln_needed} linhas totais")



def main():
    input_dataset = "/home/lucaspc/tese/uc-msc-luisv-graph_extractor/output/cfg-dataset-linux.csv"
    #input_dataset = "/home/lucaspc/tese/uc-msc-luisv-graph_extractor/output/ast-dataset-linux.csv"
    output_dataset = input_dataset.replace(".csv", "_undersampled10k.csv")

    describe_large_dataset("output/pdg-dataset-linux_undersampled10k.csv", chunksize=10000)

    
    #undersample_adaptive_chunked(input_path="output/ast-dataset-linux.csv",output_path="output/ast-dataset-linux_undersampled10k.csv",max_total=10000,min_vuln_ratio=0.2)
    

if __name__ == "__main__":
    main()
