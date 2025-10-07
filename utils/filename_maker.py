from datetime import datetime
from pathlib import Path


def get_filename(filename: str) -> str:
    file_format = filename[filename.rfind('.'):len(filename)]
    new_filename = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + file_format
    return new_filename


def get_posix_path(path: str) -> str:
    return Path(path).resolve().as_posix()