from .simple_gpg import SimpleGPG
from .simple_sops import SimpleSops, SopsError, SopsConfAWS, SopsConfGCP

import shutil

from pathlib import Path
from typing import NamedTuple

def zip_directory(base_path: Path, dir_name: str, target_path: Path):
    shutil.make_archive(f"{target_path}/{dir_name}", 'zip', base_path, dir_name)

def delete_dir(dir_path: Path):
    shutil.rmtree(dir_path)

def cleanup_dir(dir_path: Path, exceptions: list[str] = []):
    all_exceptions = [".", "..", ".gitkeep"] + exceptions

    for fs_object in dir_path.iterdir():
        if fs_object.name in all_exceptions:
            continue
        try:
            if fs_object.is_file() or fs_object.is_symlink():
                fs_object.unlink()
            elif fs_object.is_dir():
                shutil.rmtree(fs_object)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (fs_object, e))