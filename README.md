# Ollama Model Linker

This script, named `modelLink.py`, is designed to iterate through Ollama model files, creating human-readable symbolic links (symlinks) for easier access and management. It primarily targets environments where Ollama models are extensively used, providing a convenient way to reference models by more meaningful names.

## Features

- Iterates through Ollama model files located in a specified directory.
- Generates human-readable symlinks for each model, facilitating easier identification and access.
- Supports custom source (`--fromdir`) and destination (`--to`) directories for flexibility in various filesystem layouts.
- Provides functionality to clean up existing symlinks in the destination directory before creating new ones.

## Requirements

- Python 3.6 or later.
- Access to the filesystem where Ollama models are stored.

## Installation

No installation is required beyond having a Python interpreter. Simply download `modelLink.py` to a directory of your choice.

## Usage
python modelLink.py [--fromdir PATH_TO_MODELS] [--to PATH_FOR_SYMLINKS]

### Arguments

- `--fromdir`: The base directory where Ollama models are stored. Defaults to `/usr/share/ollama/.ollama/models`.
- `--to`: The directory where the model symlinks will be created. Defaults to `linkedOllamaModels` in the current directory.

### Work in progress
uploaded in case it's useful to others.
