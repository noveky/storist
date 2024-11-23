from backend.models.models import *

import typing, uuid

triples: list[Triple] = []


async def retrieve_triples(
    attr_embedding_vector=None, value_embedding_vector=None
) -> typing.AsyncGenerator[Triple, None]:
    for triple in triples:
        yield triple


async def add_triple(triple: Triple):
    triples.append(triple)


async def delete_triple_by_id(triple_id: uuid.UUID):
    for i, triple in enumerate(triples):
        if triple.item_id == triple_id:
            del triples[i]
            break


async def update_triple(triple: Triple):
    for i, t in enumerate(triples):
        if t.item_id == triple.item_id:
            triples[i] = triple
            break


async def get_triple_by_id(triple_id: uuid.UUID) -> Triple | None:
    for triple in triples:
        if triple.item_id == triple_id:
            return triple
    return None


def construct_item_object(item_id: uuid.UUID, triples: typing.Iterable[Triple]) -> Item:
    item = Item(item_id=item_id)
    for triple in triples:
        if triple.item_id == item_id:
            item.props.update({triple.attr: triple.value})
    return item


async def get_item_by_id(item_id: list[uuid.UUID]) -> Item:
    return construct_item_object(
        item_id, [triple for triple in triples if triple.item_id == item_id]
    )


async def get_items_by_ids(item_ids: list[uuid.UUID]) -> list[Item]:
    return [await get_item_by_id(item_id) for item_id in item_ids]
