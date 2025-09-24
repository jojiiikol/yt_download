from datetime import datetime


def get_filename(filename: str) -> str:
    file_format = filename[filename.rfind('.'):len(filename)]
    new_filename = datetime.now().strftime("%Y%m%d-%H%M%S") + file_format
    return new_filename
