import os

from utils import utils
from config import config
from backend.models.models import *


watch_directories = dict[str, WatchDirectory]()
watch_directories_change_handlers = []


def load_watch_directories():
    global watch_directories
    if os.path.exists(config.WATCH_DIRECTORIES_FILE):
        with open(config.WATCH_DIRECTORIES_FILE, "r", encoding="utf-8") as f:
            json_str = f.read()
        watch_directories = {
            watch_path_dict["path"]: WatchDirectory(**watch_path_dict)
            for watch_path_dict in (utils.load_json(json_str) or [])
        }


def save_watch_directories():
    with open(config.WATCH_DIRECTORIES_FILE, "w", encoding="utf-8") as f:
        f.write(utils.dump_json(list(watch_directories.values())))


def get_watch_directory_by_path(path: str) -> WatchDirectory | None:
    return watch_directories.get(os.path.normpath(path), None)


def on_watch_directories_change():
    for handler in watch_directories_change_handlers:
        handler()
    save_watch_directories()


def create_watch_directory(path: str, associated_tags: list[Tag]) -> WatchDirectory:
    watch_directory = WatchDirectory(
        path=os.path.normpath(path),
        associated_tag_ids=[tag.id for tag in associated_tags],
    )
    watch_directories[os.path.normpath(path)] = watch_directory
    on_watch_directories_change()
    return watch_directory


def delete_watch_directory(watch_directory: WatchDirectory):
    del watch_directories[watch_directory.path]
    on_watch_directories_change()


def query_all_watch_directories() -> list[WatchDirectory]:
    return list(watch_directories.values())


load_watch_directories()
