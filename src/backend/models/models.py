from dataclasses import dataclass
import typing, uuid, numpy as np, datetime


ContentType = typing.Literal["image", "text"] | None


@dataclass
class File:
    id: str
    path: str
    tag_ids: list[str]
    metadata: dict

    def to_dict(self):
        return {
            "id": self.id,
            "path": self.path,
            "tag_ids": self.tag_ids,
            "metadata": self.metadata,
        }

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
    created_at: datetime.datetime | None
    title: str
    description: str
    texts: list[str]
    tags: list[Tag]

    def from_file(file: File, tags: list[Tag]) -> "Document | None":
        return (
            Document(
                file=file,
                file_path=file.path,
                content_type=file.metadata.get("content_type", None),
                created_at=(
                    datetime.datetime.fromtimestamp(file.metadata["created_at"])
                    if "created_at" in file.metadata
                    else None
                ),
                title=file.metadata.get("title", file.path),
                description=file.metadata.get("description", ""),
                texts=file.metadata.get("texts", []),
                tags=tags,
            )
            if file.metadata.get("content_type", None) is not None
            else None
        )

    def to_dict(self):
        return {
            "file_id": self.file.id,
            "file_path": self.file_path,
            "content_type": self.content_type,
            "created_at": self.created_at,
            "title": self.title,
            "description": self.description,
            "texts": self.texts,
            "tags": [tag.name for tag in self.tags],
        }

    def __repr__(self):
        return f"Document({repr(self.to_dict())})"
