import os, uuid

from utils import utils
from config import config
from backend.models.models import *
from backend.nlp import embedding_handler


files = dict[str, File]()
watch_directories = dict[str, WatchDirectory]()


def load_files():
    global files
    if os.path.exists(config.FILES_FILE):
        with open(config.FILES_FILE, "r") as f:
            files = {
                file_dict["id"]: File(**file_dict) for file_dict in utils.load_json(f)
            }


def load_watch_directories():
    global watch_directories
    if os.path.exists(config.WATCH_DIRECTORIES_FILE):
        with open(config.WATCH_DIRECTORIES_FILE, "r") as f:
            watch_directories = {
                watch_path_dict["path"]: WatchDirectory(**watch_path_dict)
                for watch_path_dict in utils.load_json(f)
            }


def save_files():
    with open(config.FILES_FILE, "w") as f:
        f.write(utils.dump_json(files.values(), indent=4))


def save_watch_directories():
    with open(config.WATCH_DIRECTORIES_FILE, "w") as f:
        f.write(utils.dump_json(watch_directories.values(), indent=4))


def new_file_id():
    return str(uuid.uuid4())


def get_file_by_id(file_id: str) -> File | None:
    return files.get(file_id, None)


def get_file_by_path(file_path: str) -> File | None:
    for id, path in files.items():
        if path == file_path:
            return id
    return None


def get_watch_path_by_path(path: str) -> WatchDirectory | None:
    return watch_directories.get(path, None)


def create_file(file_path: str) -> File:
    file_id = new_file_id()
    file = File(id=file_id, path=file_path)
    files[file_id] = file
    save_files()
    return file


def delete_file(file_path: str):
    file_id = get_file_by_path(file_path)
    if file_id:
        del files[file_id]
        save_files()


def move_file(src_path: str, dest_path: str):
    file_id = get_file_by_path(src_path)
    if file_id:
        files[file_id].path = dest_path
        save_files()


def save_file_metadata(file_path: str, metadata: dict):
    files[get_file_by_path(file_path).id].metadata = metadata
    save_files()


def change_watch_directories(new_watch_directories):
    global watch_directories

    for path in watch_directories:
        if path not in new_watch_directories:
            del watch_directories[path]

    for path in new_watch_directories:
        if path not in watch_directories:
            watch_directories[path] = WatchDirectory(path=path)

    save_watch_directories()


def query_most_relevant_files(
    query_description_embedding: np.ndarray, max_num: int | None = None
) -> list[File]:
    scores = []
    for file in files.values():
        if (
            file.metadata
            and (
                description_embedding := file.metadata.get(
                    "description_embedding", None
                )
            )
            is not None
        ):
            score = embedding_handler.cosine_similarity(
                query_description_embedding, description_embedding
            )
            scores.append((file, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    if max_num:
        scores = scores[:max_num]
    return [file for file, _ in scores]


files = load_files()
watch_directories = load_watch_directories()
