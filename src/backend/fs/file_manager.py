from . import file_system_watcher

from utils import utils
from config import config
from backend.preprocessing import preprocessing_handler

import typing, os, uuid, asyncio, threading


watcher = None
files: "dict[str, File]" = {}


def new_file_id():
    return str(uuid.uuid4())


class File:
    def __init__(
        self,
        path: str,
        id: str | None = None,
        metadata: typing.Any | None = None,
    ):
        self.id = id or new_file_id()
        self.path = path
        self.metadata = metadata

    def to_dict(self):
        return {"id": self.id, "path": self.path, "metadata": self.metadata}


def get_file_by_id(file_id: str) -> File:
    return files[file_id]


def get_file_by_path(path: str) -> File:
    for file_id, file_path in files.items():
        if file_path == path:
            return file_id
    return None


def load_files() -> dict[str, File]:
    files = {}
    if os.path.exists(config.FILES_FILE):
        with open(config.FILES_FILE, "r") as f:
            files = {
                file_dict["id"]: File(**file_dict) for file_dict in utils.load_json(f)
            }
    return files


def load_dirs() -> list[str]:
    dirs = []
    if os.path.exists(config.DIRS_FILE):
        with open(config.DIRS_FILE, "r") as f:
            dirs = utils.load_json(f)
    return dirs


def save_files(files: dict):
    with open(config.FILES_FILE, "w") as f:
        utils.dump_json(files.values(), f, indent=4)


def save_directories(dirs: list):
    with open(config.DIRS_FILE, "w") as f:
        utils.dump_json(dirs, f, indent=4)


def preprocess_file(path):
    async def run_preprocessing():
        result = await preprocessing_handler.preprocess_file(path)
        files[get_file_by_path(path).id].metadata = result

    thread = threading.Thread(target=lambda: asyncio.run(run_preprocessing()))
    thread.start()


def create_event_handler(path):
    print(f"File created: {path}")
    file_id = new_file_id()
    files[file_id] = File(id=file_id, path=path)
    save_files(files)

    preprocess_file(path)


def delete_event_handler(path):
    print(f"File deleted: {path}")
    for file_id, file_path in files.items():
        if file_path == path:
            files.pop(file_id)
            break
    save_files(files)


def modify_event_handler(path):
    print(f"File modified: {path}")
    preprocess_file(path)


def move_event_handler(src_path, dest_path):
    print(f"File moved: {src_path} -> {dest_path}")
    for file_id, file_path in files.items():
        if file_path == src_path:
            files[file_id] = dest_path
            break
    save_files(files)


def start_watcher(watch_paths):
    global watcher

    watcher = file_system_watcher.FileSystemWatcher(
        watch_paths,
        create_event_handler=create_event_handler,
        delete_event_handler=delete_event_handler,
        modify_event_handler=modify_event_handler,
        move_event_handler=move_event_handler,
    )
    watcher.start()


def change_watch_paths(watch_paths):
    for path in watcher.paths:
        if path not in set(watch_paths):
            watcher.remove_path(path)

    for path in watch_paths:
        if path not in watcher.paths:
            watcher.add_path(path)

    save_directories(watch_paths)


files = load_files()
dirs = load_dirs()
start_watcher(dirs)
