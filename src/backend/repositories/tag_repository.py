import os, uuid

from utils import utils
from config import config
from backend.models.models import *


tags = dict[str, Tag]()


def load_tags():
    global tags
    if os.path.exists(config.TAGS_FILE):
        with open(config.TAGS_FILE, "r", encoding="utf-8") as f:
            json_str = f.read()
        tags = {
            tag_dict["id"]: Tag(**tag_dict)
            for tag_dict in (utils.load_json(json_str) or [])
        }


def save_tags():
    with open(config.TAGS_FILE, "w", encoding="utf-8") as f:
        f.write(utils.dump_json(tags.values()))


def new_tag_id():
    return str(uuid.uuid4())


def get_tag_by_id(tag_id: str) -> Tag:
    return tags[tag_id]


def get_tags_by_ids(tag_ids: list[str]) -> list[Tag]:
    return [tags[tag_id] for tag_id in tag_ids]


def create_tag(tag_name: str) -> Tag:
    tag_id = new_tag_id()
    tag = Tag(id=tag_id, name=tag_name)
    tags[tag_id] = tag
    save_tags()
    return tag


def delete_tag(tag_id: str):
    del tags[tag_id]
    save_tags()


def query_tags_by_prefix(prefix: str) -> list[Tag]:
    return [tag for tag in tags.values() if tag.name.startswith(prefix)]


load_tags()
