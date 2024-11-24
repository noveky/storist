import os


DATA_DIR = "data"
FILES_FILE = os.path.join(DATA_DIR, "files.json")
WATCH_DIRECTORIES_FILE = os.path.join(DATA_DIR, "watch_directories.json")
FILE_STATES_FILE = os.path.join(DATA_DIR, "file_states.json")

os.makedirs(DATA_DIR, exist_ok=True)
