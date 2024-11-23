from ..db import database
from ..db.models import *
from . import graph_query_executor, graph_query_interpreter, semantic_query_executor

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

    # Graph query
    sql_select_stmt = await graph_query_interpreter.interpret_query(query)
    graph_query_result_ids_with_scores = await graph_query_executor.execute_graph_query(
        sql_select_stmt
    )
    graph_query_result_ids_with_scores = graph_query_result_ids_with_scores[
        :MAX_ITEM_COUNT
    ]

    # Merge and sort results by score
    merged_sorted_result_ids = merge_and_sort_query_results(
        semantic_query_result_ids_with_scores, graph_query_result_ids_with_scores
    )

    # Convert to item objects
    result_items = await database.get_items_by_ids(
        item_id for item_id, _ in merged_sorted_result_ids
    )

    return result_items
