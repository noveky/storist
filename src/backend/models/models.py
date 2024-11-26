from dataclasses import dataclass
import typing, uuid, numpy as np, datetime


ContentType = typing.Literal["image", "text"] | None


@dataclass
class Triple:
    triple_id: uuid.UUID
    item_id: uuid.UUID
    attr: str
    attr_embedding_vector: np.ndarray
    value: str
    value_embedding_vector: np.ndarray


@dataclass
class Item:
    item_id: uuid.UUID
    props: dict

    def update_props(self, triple: Triple):
        self.props[triple.attr] = triple.value

    def __repr__(self):
        all_props = self.props
        all_props.update({"id": self.item_id})
        prop_list_str = ", ".join([f"{k}={repr(v)}" for k, v in all_props.items()])
        return f"Item({prop_list_str})"


@dataclass
class File:
    id: str
    path: str
    metadata: dict

    def to_dict(self):
        return {"id": self.id, "path": self.path, "metadata": self.metadata}

    def __repr__(self):
        return f"File({repr(self.to_dict())})"


@dataclass
class WatchDirectory:
    path: str
    associated_tag_ids: list[str]

    def to_dict(self):
        return {"path": self.path, "associated_tag_ids": self.associated_tag_ids}

    def __repr__(self):
        return f"WatchDirectory({repr(self.to_dict())})"


@dataclass
class Tag:
    id: str
    name: str

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"Tag({repr(self.to_dict())})"


@dataclass
class DataSource:
    watch_directory: WatchDirectory
    associated_tags: list[Tag]

    def from_watch_directory(
        watch_directory: WatchDirectory, associated_tags: list[Tag]
    ) -> "DataSource":
        return DataSource(
            watch_directory=watch_directory, associated_tags=associated_tags
        )

    def to_dict(self):
        return {
            "watch_directory": self.watch_directory.to_dict(),
            "associated_tags": [tag.name for tag in self.associated_tags],
        }

    def __repr__(self):
        return f"DataSource({repr(self.to_dict())})"


@dataclass
class Document:
    file: File
    file_path: str
    content_type: ContentType
    date: str
    title: str
    description: str
    tags: list[Tag]

    def from_file(file: File, tags: list[Tag]) -> "Document":
        return Document(
            file=file,
            file_path=file.path,
            content_type=file.metadata["content_type"],
            date=datetime.datetime.fromtimestamp(
                file.metadata["datetime_created"]
            ).strftime(r"%Y-%m-%d %H:%M:%S"),
            title=file.metadata["title"],
            description=file.metadata["description"],
            tags=tags,
        )

    def to_dict(self):
        return {
            "file_id": self.file.id,
            "file_path": self.file_path,
            "content_type": self.content_type,
            "date": self.date,
            "title": self.title,
            "description": self.description,
            "tags": [tag.name for tag in self.tags],
        }

    def __repr__(self):
        return f"Document({repr(self.to_dict())})"
