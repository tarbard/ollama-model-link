import os
import json
from pathlib import Path
import argparse
import sys

parser = argparse.ArgumentParser(description="Create human readable symlinks to Ollama models")
parser.add_argument('--fromdir', type=str, default="/usr/share/ollama/.ollama/models",
                    help='Base directory where models are stored e.g /usr/share/ollama/.ollama/models')
parser.add_argument('--to', type=str, default="linkedOllamaModels",
                    help='Directory where model links will be created e.g linkedOllamaModels')

args = parser.parse_args()

base_dir = Path(args.fromdir)
linked_model_location = Path(args.to)

if not base_dir.is_dir():
    print(f"Error: fromdir {base_dir} does not exist.")
    sys.exit(1)

manifest_dir = base_dir / 'manifests' / 'registry.ollama.ai'
blob_dir = base_dir / 'blobs'


def delete_symlinks(directory):
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.islink(item_path):
            try:
                os.remove(item_path)
                print(f"Removed symlink: {item_path}")
            except OSError as e:
                print(f"Error removing {item_path}: {e}")


def process_file(file_path, blob_dir, publicmodels_dir):
    print(file_path)
    user = file_path.parts[-3].replace('registry.ollama.ai', 'ollama')
    model = file_path.parts[-2]
    tag = file_path.name

    with open(file_path, 'r') as file:
        data = json.load(file)

    for layer in data.get('layers', []):
        if layer.get('mediaType') == 'application/vnd.ollama.image.model':
            digest = layer.get('digest')
            create_symlink(blob_dir, digest, publicmodels_dir, user, model, tag)


def create_symlink(blob_dir, digest, publicmodels_dir, user, model, tag):
    source = blob_dir / digest
    if user == "library":
        destination = publicmodels_dir / f"{model}-{tag}.gguf"
    else:
        destination = publicmodels_dir / f"{user}-{model}-{tag}.gguf"

    destination.symlink_to(source)
    print(f"Created link of {user} - {model}:{tag} at {destination}")


linked_model_location.mkdir(parents=True, exist_ok=True)
delete_symlinks(linked_model_location)

for file_path in manifest_dir.glob('**/*'):
    print(f"looking at {file_path}")
    if file_path.is_file() and len(file_path.parts) - len(manifest_dir.parts) == 3:
        process_file(file_path, blob_dir, linked_model_location)
