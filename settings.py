import os


from utils.filename_maker import get_posix_path

MEDIA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "media")
POSIX_MEDIA_DIR = get_posix_path(MEDIA_DIR)

