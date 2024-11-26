from backend.repositories import triple_repository
from backend.models.models import *
from . import (
    semantic_query_executor,
    structured_query_executor,
    structured_query_interpreter,
)

import datetime

MIN_SCORE = 0.5
MAX_ITEM_COUNT = 10


def assemble_and_sort_query_results(*results: list[tuple[Document, float]]):
    # Combine results from multiple sources
    result_map = {}

    for result in results:
        for doc, score in result:
            result_map[doc.file.id] = result_map.get(doc.file.id, 0) + score

    return sorted(result_map.items(), key=lambda x: x[1], reverse=True)


async def handle_query(
    query_content_type: str | None,
    query_title: str | None,
    query_description: str | None,
    query_date_from: datetime.date | None,
    query_date_to: datetime.date | None,
    min_score: float = MIN_SCORE,
    max_item_count: int = MAX_ITEM_COUNT,
) -> list[Document]:

    result_group = []

    # Semantic queries
    if query_title:
        title_query_result_ids_with_scores = (
            await semantic_query_executor.execute_semantic_query(
                query_type="title", query_text=query_title
            )
        )
        result_group.append(title_query_result_ids_with_scores)
    if query_description:
        description_query_result_ids_with_scores = (
            await semantic_query_executor.execute_semantic_query(
                query_type="description", query_text=query_description
            )
        )
        result_group.append(description_query_result_ids_with_scores)

    # # Structured query
    # psql_select_stmt = await structured_query_interpreter.interpret_query(query)
    # structured_query_result_ids_with_scores = (
    #     await structured_query_executor.execute_structured_query(psql_select_stmt)
    # )

    # Assemble and sort results by score
    result = assemble_and_sort_query_results(*result_group)[:max_item_count]

    # Convert to document objects
    result_docs = await triple_repository.get_items_by_ids(
        item_id for item_id, score in result if score >= min_score
    )

    return result_docs
