from backend.db import database
from backend.models.models import *
from . import (
    semantic_query_executor,
    structured_query_executor,
    structured_query_interpreter,
)

MAX_ITEM_COUNT = 10


def merge_and_sort_query_results(*results: list[tuple[Item, float]]):
    # Flatten the list of results
    all_results = [elem for sublist in results for elem in sublist]

    # Sort the results by score in descending order
    sorted_results = sorted(all_results, key=lambda x: x[1], reverse=True)

    return sorted_results


async def handle_query(query: str):
    # Semantic query
    # semantic_query_result_ids = await semantic_query_executor.execute_semantic_query(
    #     query
    # )
    semantic_query_result_ids_with_scores = []

    # Structured query
    psql_select_stmt = await structured_query_interpreter.interpret_query(query)
    structured_query_result_ids_with_scores = (
        await structured_query_executor.execute_structured_query(psql_select_stmt)
    )
    structured_query_result_ids_with_scores = structured_query_result_ids_with_scores[
        :MAX_ITEM_COUNT
    ]

    # Merge and sort results by score
    merged_sorted_result_ids = merge_and_sort_query_results(
        semantic_query_result_ids_with_scores, structured_query_result_ids_with_scores
    )

    # Convert to item objects
    result_items = await database.get_items_by_ids(
        item_id for item_id, _ in merged_sorted_result_ids
    )

    return result_items
