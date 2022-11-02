import json
import os
import shutil
from pathlib import Path

from scripts.dates import CustomDatesEncoder


def file_list(directory):
    return Path(directory).iterdir()


def file_exists(path):
    return Path(path).is_file()


def json_dump(path, json_content):
    if json_content and path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f2:
            json.dump(json_content, f2, ensure_ascii=False, indent=4, cls=CustomDatesEncoder)


def safe_read(input_file):
    res = None
    if file_exists(input_file):
        with open(input_file, 'r') as f:
            res = f.read()
    return res


def safe_read_as_json(input_file, decoder):
    content = safe_read(input_file)
    if content:
        return json.loads(content, cls=decoder)
    else:
        return None


def clear_dir(directory):
    shutil.rmtree(directory, ignore_errors=True)
