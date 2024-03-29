# Ollama Model Linker

This script, named `modelLink.py`, is designed to iterate through Ollama model files, creating human-readable symbolic links (symlinks) for easier access and management. It primarily targets environments where Ollama models are extensively used, providing a convenient way to reference models by more meaningful names.

## Features

- Iterates through Ollama model files located in a specified directory.
- Generates human-readable symlinks for each model, facilitating easier identification and access.
- Supports custom source (`--fromdir`) and destination (`--to`) directories for flexibility in various filesystem layouts.
- Provides functionality to clean up existing symlinks in the destination directory before creating new ones.
- Optionally can find the models present on HuggingFace and use the metadata to create symlinks filenames and/or a directory structure compatible with LM Store

## Requirements

- Python 3.9 or later.
- Access to the filesystem where Ollama models are stored.
- Hugging Face API library: `pip install huggingface_hub`

## Installation

No installation is required beyond having a Python interpreter. Simply download `modelLink.py` to a directory of your choice.
The HuggingFace Hub API library must be installed to use the related features.

## Usage
python modelLink.py [--fromdir PATH_TO_MODELS] [--to PATH_FOR_SYMLINKS] [--hf] [--lms] [--refresh]

### Arguments

- `--fromdir`: The base directory where Ollama models are stored. Defaults to `/usr/share/ollama/.ollama/models` on Linux, autodetected on all platforms. Automatic detection override by `OLLAMA_MODELS` environment variable.
- `--to`: The directory where the model symlinks will be created. Defaults to `linkedOllamaModels` in the current directory.
- `--hf`: Retrieve and use the HF metadata to create the model symlinks filenames
- `--lms`: Retrieve and use the HF metadata to create the model symlinks directory structure and filenames in an LM Store format
- `--cleanup`: Remove all the existing links and exit
- `-r`, `--refresh`: Ignore the "not found" cached HF metadata and try to find the models again
- `-v`, `--version`: Print out the script version

### Work in progress
uploaded in case it's useful to others.

### ChangeLog

v0.3:
- Added `--cleanup` and `--version` arguments
- Detection of model path using `OLLAMA_MODELS` environment variable
v0.2:
- Added support for automatic default paths for Linux, MacOS and Windows
- Added support for Windows using hard links