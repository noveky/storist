import os, uuid

from utils import utils
from config import config
from backend.models.models import *
from backend.nlp import embedding_handler


files = dict[str, File]()


def load_files():
    global files
    if os.path.exists(config.FILES_FILE):
        with open(config.FILES_FILE, "r", encoding="utf-8") as f:
            json_str = f.read()
        files = {
            file_dict["id"]: File(**file_dict)
            for file_dict in (utils.load_json(json_str) or [])
        }


def save_files():
    with open(config.FILES_FILE, "w", encoding="utf-8") as f:
        f.write(utils.dump_json(list(files.values())))


def new_file_id():
    return str(uuid.uuid4())


def get_file_by_id(file_id: str) -> File | None:
    return files.get(file_id, None)


def get_file_by_path(file_path: str) -> File | None:
    for file in files.values():
        if file.path == os.path.normpath(file_path):
            return file
    return None


def create_file(file_path: str) -> File:
    file_id = new_file_id()
    file = File(id=file_id, path=os.path.normpath(file_path), tag_ids=[], metadata={})
    files[file_id] = file
    save_files()
    return file


def get_or_create_file(file_path: str) -> File:
    if file := get_file_by_path(file_path):
        return file
    return create_file(file_path)


def delete_file(file_path: str):
    file = get_file_by_path(file_path)
    if file:
        file_id = file.id
        del files[file_id]
        save_files()


def move_file(src_path: str, dest_path: str):
    file = get_file_by_path(src_path)
    if file:
        files[file.id].path = dest_path
        save_files()


def save_file_metadata(file_path: str, metadata: dict):
    file = get_file_by_path(file_path)
    if file:
        files[file.id].metadata = metadata
        save_files()
        print(f"Saved metadata for file: {file_path}")


def query_all_files() -> list[File]:
    return list(files.values())


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


load_files()
