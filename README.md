# Graph Extraction Pipeline

End to end graph extraction and feature building for CFG, AST, and PDG from open source C projects, ready for downstream DGCNN based classification.

## What this repo does

1. Checks out specific commits from a local clone of an open source project
2. Uses Joern to export graph representations per file or per function
3. Generates two artefacts per graph
   a copy of the original DOT
   a TXT file with node statements labels taken from DOT attributes
4. Converts each graph to adjacency and feature matrices and writes a CSV dataset

The pipeline preserves full graphs by default so you keep structural richness. No slicing is applied in the default flow.&#x20;

## Key scripts

1. main.py orchestrates the whole flow. It loads commit to file mappings, extracts graphs with Joern, creates unreduced DOT and statements artefacts, and builds the final CSV datasets.&#x20;
2. cfg\_extraction.py wraps Joern and exports CFG, AST, or PDG, either for a whole repo or for a specific file list per commit.&#x20;
3. reduce\_cfg\_batch.py writes unreduced DOT plus statement TXT files for each graph, and also contains the optional reducer.&#x20;
4. reduce\_graph.py contains the node merge reducer and the writers for DOT and statements.&#x20;
5. cfg\_feature\_extraction.py converts DOT to NetworkX, builds adjacency A and feature matrix X for cfg ast pdg, and writes CSV rows.&#x20;
6. utils.py has dataset utilities such as undersampling and quick stats.&#x20;

## Requirements

1. Joern CLI installed and accessible on PATH
2. Python 3 with networkx numpy pandas and graphviz Python bindings
3. A local git clone of the target open source project with full history

Set the Joern path if needed in cfg\_extraction.py through JOERN\_CLI\_DIR or ensure joern-parse and joern-export are on PATH.&#x20;

## Configure paths

Open main.py and adjust

1. base\_project\_directory points to the folder that holds your project clone
2. commit\_data\_directory points to the folder with the metadata CSV
3. commit\_data is the CSV filename with file paths per vulnerable commit
4. base\_output\_directory is where all outputs will be written

All of these appear at the top of main.py.&#x20;

## Input metadata CSV

The pipeline expects a CSV with at least

1. Vulnerable Commit Hash
2. File Path

main.py reads this file to compute the set of commits and the file list per commit.&#x20;

## Quick start

1. Activate your environment
2. Configure the paths in main.py
3. Pick the graph types to extract in graph\_type\_list for example cfg ast pdg
4. Run the pipeline

   python main.py

The default flow for each commit is

1. Extract graphs per file with Joern
2. Generate unreduced DOT and per node statements TXT
3. Build adjacency and feature matrices and write the CSV dataset

All three steps are called in main.py through extract\_cfg\_per\_commit\_file then generate\_unreduced\_graph\_artifacts then fex\_read\_graph\_file.&#x20;

## What gets created

Under base\_output\_directory the pipeline creates per commit folders of the form

1. output cfg commit
2. output ast commit
3. output pdg commit

For each graph you will see

1. A DOT file in project graphtype reduced output commit path graphname.dot
2. A TXT file in project graphtype statements output commit path graphname.txt

These are written by reduce\_cfg\_batch.generate\_unreduced\_graph\_artifacts using write\_dot\_file and write\_statement\_file.

Datasets are written under output as CSV files named like

1. cfg dataset project.csv
2. ast dataset project.csv
3. pdg dataset project.csv

Rows contain graph filepath label size flattened adjacency and flattened features. See cfg\_feature\_extraction.write\_cfgs\_to\_file and the fex\_read\_graph\_file call chain.&#x20;

## How graphs are extracted

cfg\_extraction.py uses Joern commands

1. joern-parse to ingest C files
2. joern-export to emit the chosen representation cfg ast pdg

You can run per repository or per file. The per file path is used when you want to limit extraction to the exact files touched in each commit.&#x20;

## Features per graph type

The matrices A and X are built in cfg\_feature\_extraction.py

1. Common step convert DOT to NetworkX and build A with node order maintained.&#x20;
2. CFG features combine
   a vertex structure out degree in degree number of statements
   b code sequence counts of instruction types
   c memory management cues such as allocation deallocation unsafe string and scanf usage and address of operator.&#x20;
3. AST features include literal identifier call block control structure unknown leaf flag and out degree.&#x20;
4. PDG features include DDG out and in CDG out and in control dependency flag total edges and parameter flag.&#x20;

Node statements are read from the DOT attributes and stored in the TXT artefact earlier in the pipeline. These statements drive the per node feature extraction.

## Optional graph reduction

If you need reduced graphs you can switch to reduce\_read\_cfg\_file which merges linear chains while preserving control structure. It outputs a merged DOT and a statement file per merged node. This is not enabled in the default flow that preserves full graphs.

## Resume and skip logic

The extraction step and the artefact generation step both skip work when output folders already exist. This lets you rerun safely without reprocessing completed commits.

## Utilities

utils.py includes

1. describe\_large\_dataset for quick stats on big CSVs
2. undersample\_adaptive\_chunked to create balanced subsets without loading everything in memory
3. helpers to find largest graphs and to check presence of memory management features

These are handy for sanity checks before training.&#x20;

## Troubleshooting

1. Joern not found
   ensure JOERN\_CLI\_DIR is correct in cfg\_extraction.py or joern tools are on PATH.&#x20;
2. Graphs not being written
   confirm your commit metadata has valid file paths for that commit and that the repo is checked out by version management before extraction main.py calls load\_commit for this.&#x20;
3. CSV grows very large
   use utils.describe\_large\_dataset and utils.undersample\_adaptive\_chunked to get summaries and to sample a manageable subset.&#x20;

## Minimal example flow

1. Place your project clone under base\_project\_directory

2. Put the metadata CSV under commit\_data\_directory with columns Vulnerable Commit Hash and File Path

3. In main.py set graph\_type\_list to cfg or ast or pdg

4. Run

   python main.py

5. Find DOT and TXT artefacts under project graphtype reduced and project graphtype statements

6. Find the CSV dataset under output named graphtype dataset project.csv

