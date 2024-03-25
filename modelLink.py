import os
import json
from pathlib import Path
import argparse
import sys
from contextlib import contextmanager

@contextmanager
def optional_dependencies(error: str = "ignore"):
    assert error in {"raise", "warn", "ignore"}
    try:
        yield None
    except ImportError as e:
        if error == "raise":
            raise e
        if error == "warn":
            msg = f'Missing optional dependency "{e.name}". Use pip or conda to install.'
            print(f'Warning: {msg}')

hf_hub = 0
with optional_dependencies("ignore"):
    from huggingface_hub import HfApi
    hf_api = HfApi()
    hf_hub = 1

if bool(hf_hub):
    print("HuggingFace Hub API library found")

parser = argparse.ArgumentParser(description="Create human readable symlinks to Ollama models")
parser.add_argument('--fromdir', type=str, default="/usr/share/ollama/.ollama/models",
                    help='Base directory where models are stored e.g /usr/share/ollama/.ollama/models')
parser.add_argument('--to', type=str, default="linkedOllamaModels",
                    help='Directory where model links will be created e.g linkedOllamaModels')
parser.add_argument('--lms', action='store_true',
                    help='Enable creating symlinks in LM Studio format, the HuggingFace Hub API library must be installed')
parser.add_argument('--hf', action='store_true',
                    help='Enable creating symlinks using HF filenames, the HuggingFace Hub API library must be installed')
parser.add_argument('--refresh', action='store_true',
                    help='Lookup again all models cached as not availabe on HF, the HuggingFace Hub API library must be installed')

args = parser.parse_args()

base_dir = Path(args.fromdir)
linked_model_location = Path(args.to)
lms_store = args.lms
hf_refresh = args.refresh
hf_store = args.hf
hf_cache = f'{linked_model_location}/.hf_cache'

if bool(lms_store) or bool(hf_store):
    if not bool(hf_hub):
        print(f"Error: --hf and --lms options needs the HuggingFace Hub API library. Use pip or conda to install.")
        sys.exit(1)
    cached_data = {}
    if os.path.isfile(hf_cache):
        print(f"Loading cached HF repos from: {hf_cache}")
        with open(hf_cache, 'r') as hfc:
            cached_data = json.load(hfc)

if not base_dir.is_dir():
    print(f"Error: fromdir {base_dir} does not exist.")
    sys.exit(1)

manifest_dir = base_dir / 'manifests' / 'registry.ollama.ai'
blob_dir = base_dir / 'blobs'

def delete_symlinks(directory):
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    for root, dirs, files in os.walk(directory, topdown=True):
        for file in files:
            if os.path.islink(os.path.join(root, file)):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"Removed symlink: {file}")
                    files.remove(file)
                except OSError as e:
                    print(f"Error removing symlink {file}: {e}")
        for dir in dirs:
            delete_symlinks(os.path.join(root, dir))
            if not os.listdir(os.path.join(root, dir)):
                try:
                    os.rmdir(os.path.join(root, dir))
                    dirs.remove(dir)
                except OSError as e:
                    print(f"Error removing empty directory {dir}: {e}")

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

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
            hash = digest[7:]
            print(f"File sha256: {hash}")
            if bool(hf_store) or bool(lms_store):
                model_id = False
                model_author = False
                model_filename = False
                model_name = False
                model_found = False
                model_id = cached_data.get(hash)
                if model_id != 0:
                    model_author = cached_data.get(f'{hash}_author')
                    model_filename = cached_data.get(f'{hash}_filename')
                elif model_id == 0 and not bool(hf_refresh):
                    print(f'Model "{model}:{tag}" lookup skipped, cached as not available on HF')
                else:
                    modelsearch = f'{model} gguf'
                    modelcount = 0
                    models = hf_api.list_models(search=modelsearch, full=True, cardData=False, sort='downloads', direction=-1)
                    print(f'"{model}:{tag}" not found in cache, searching for "{modelsearch}" on HF...')
                    for model_item in models:
                        repo_hash = False
                        repo_query = True
                        try:
                            repo_tree = hf_api.list_repo_tree(model_item.id, expand=True, recursive=False)
                        except Exception as e:
                            repo_query = False
                        if bool(repo_query):
                            try:
                                for repo_item in repo_tree:
                                    try:
                                        repo_hash = repo_item.lfs.sha256
                                        if hash == repo_hash:
                                            print(f'Model is PRESENT on HF as {model_item.id} Filename={repo_item.path} Likes={model_item.likes} Down={model_item.downloads}')
                                            model_id = model_item.id
                                            model_author = model_item.author
                                            model_filename = repo_item.path
                                            model_found = True
                                            continue
                                    except Exception as e:
                                        repo_hash = False
                                    modelcount += 1
                            except Exception as e:
                                model_found = False
                    print(f'Model "{modelsearch}" lookup over {modelcount} models finished')
                    if bool(model_found):
                        cached_data[hash] = model_id
                        cached_data[f'{hash}_author'] = model_author
                        cached_data[f'{hash}_filename'] = model_filename
                        print(f'Model "{model}:{tag}" cached as {model_id}/{model_filename}')
                    else:
                        model_id = 0
                        cached_data[hash] = model_id
                        print(f'Model "{model}:{tag}" cached as not available on HF')
                if model_id == 0:
                    model_filename = None
                    model_author = None
                if bool(hf_store):
                    create_symlink_hf(blob_dir, digest, publicmodels_dir, user, model, tag, model_id, model_author, model_filename, False)
                if bool(lms_store):
                    create_symlink_hf(blob_dir, digest, publicmodels_dir, user, model, tag, model_id, model_author, model_filename, True)
            else:
                create_symlink(blob_dir, digest, publicmodels_dir, user, model, tag)

def create_symlink_hf(blob_dir, digest, publicmodels_dir, user, model, tag, model_id, model_author, model_filename, lms):
    source = blob_dir / digest
    this_author = model_author
    this_filename = model_filename
    this_id = model_id

    if model_id == 0:
        if user == 'library':
            this_author = 'oolama-ai'
            this_filename = f'{model}-{tag}.gguf'
        else:
            this_author = f'{user}'
            this_filename = f'{model}-{tag}.gguf'
        this_id = f'{this_author}/{model}'

    if bool(lms):
        if not os.path.exists( publicmodels_dir / this_author ):
            os.makedirs( publicmodels_dir / this_author )
        if not os.path.exists( publicmodels_dir / this_id ):
            os.makedirs( publicmodels_dir / this_id )
        destination = publicmodels_dir / this_id / this_filename
    else:
        destination = publicmodels_dir / f'{this_author}-{this_filename}'

    if os.path.isfile(destination) or os.path.islink(destination):
        os.remove(destination)
    destination.symlink_to(source)
    print(f"Created link of {user} - {model}:{tag} at {destination}")

def create_symlink(blob_dir, digest, publicmodels_dir, user, model, tag):
    source = blob_dir / digest
    if user == "library":
        destination = publicmodels_dir / f"{model}-{tag}.gguf"
    else:
        destination = publicmodels_dir / f"{user}-{model}-{tag}.gguf"

    if os.path.isfile(destination) or os.path.islink(destination):
        os.remove(destination)
    destination.symlink_to(source)
    print(f"Created link of {user} - {model}:{tag} at {destination}")


linked_model_location.mkdir(parents=True, exist_ok=True)
delete_symlinks(linked_model_location)

for file_path in manifest_dir.glob('**/*'):
    print(f"Looking at {file_path}")
    if file_path.is_file() and len(file_path.parts) - len(manifest_dir.parts) == 3:
        process_file(file_path, blob_dir, linked_model_location)

if bool(hf_store) or bool(lms_store):
    with open(hf_cache, 'w') as hfc:
        json.dump(cached_data, hfc)
