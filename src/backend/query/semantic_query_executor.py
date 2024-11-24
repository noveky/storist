from backend.models.models import *
from backend.repositories import triple_repository
from backend.nlp import embedding_handler


async def execute_semantic_query(query: str):
    # Embed the query
    query_vector = await embedding_handler.get_text_embeddings([query])[0]

    # Retrieve all triples
    triples = triple_repository.retrieve_triples()

    # Populate item_ids and item_triples_map
    item_ids = set()
    item_triples_map: dict[int, list[Triple]] = {}
    async for triple in triples:
        item_ids.add(triple.item_id)
        if triple.item_id not in item_triples_map:
            item_triples_map[triple.item_id] = []
        item_triples_map[triple.item_id].append(triple)

    # Compute the score for each item
    item_score_map = {}
    for item_id in item_ids:
        item = triple_repository.construct_item_object(
            item_id, item_triples_map[item_id]
        )
        item_score_map[item_id] = embedding_handler.cosine_similarity(
            query_vector, item.props["semantic_embedding_vector"]
        )

    # Zip the item ids with their corresponding scores
    item_ids_with_scores = [(sid, item_score_map[sid]) for sid in item_ids]

    return item_ids_with_scores
