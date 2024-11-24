from dataclasses import dataclass
import typing, uuid, numpy as np


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
    metadata: dict | None = None

    def to_dict(self):
        return {"id": self.id, "path": self.path, "metadata": self.metadata}

    def __repr__(self):
        return f"File({repr(self.to_dict())})"


@dataclass
class WatchDirectory:
    path: str

    def to_dict(self):
        return {"path": self.path}

    def __repr__(self):
        return f"WatchDirectory({repr(self.to_dict())})"
