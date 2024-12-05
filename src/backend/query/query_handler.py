from backend.repositories import file_repository, tag_repository
from backend.models.models import *
from . import (
    nl_query_interpreter,
    semantic_query_executor,
    structured_query_executor,
)

import datetime, numpy as np
from sklearn.cluster import KMeans

MAX_ITEM_COUNT = 10


def cutoff_results(result_docs_with_scores, num_clusters=2):
    scores = np.array(
        [score for _, score in result_docs_with_scores if score > 0]
    ).reshape(-1, 1)
    print(f"Non-zero scores:\n{scores}")

    if scores.shape[0] < num_clusters:
        print("Not enough results to cluster")
        return [
            result_doc_with_score
            for result_doc_with_score in result_docs_with_scores
            if result_doc_with_score[1] > 0
        ]

    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(scores)
    cluster_labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_.flatten()

    # Identify the cluster with the highest center
    highest_cluster = np.argmax(cluster_centers)
    min_score = min(scores[cluster_labels == highest_cluster])

    print("Clustering result:")
    print(f"High cluster:\n{scores[cluster_labels == highest_cluster]}")
    print(f"Low cluster:\n{scores[cluster_labels != highest_cluster]}")

    return [doc for doc, score in result_docs_with_scores if score >= min_score]


def assemble_and_sort_query_results(*results: list[tuple[Document, float]]):
    # Combine results from multiple sources
    result_map = {}
    doc_map = {}

    for result in results:
        for doc, score in result:
            doc_map[doc.file.id] = doc
            result_map[doc.file.id] = result_map.get(doc.file.id, 1) * score

    result_ids_with_scores = sorted(
        result_map.items(), key=lambda x: x[1], reverse=True
    )
    result_docs_with_scores = [
        (doc_map[doc_id], score) for doc_id, score in result_ids_with_scores
    ]

    return result_docs_with_scores


async def handle_nl_query(
    specification: str,
    max_item_count: int = MAX_ITEM_COUNT,
) -> list[Document]:
    # Interpret query
    ssql_select_stmt = await nl_query_interpreter.interpret_query(specification)

    # Execute query
    result_docs_with_scores = await structured_query_executor.execute_structured_query(
        ssql_select_stmt
    )

    # Sort results
    result_docs_with_scores = sorted(
        result_docs_with_scores, key=lambda x: x[1], reverse=True
    )

    # Cut off results
    result_docs = cutoff_results(result_docs_with_scores)[:max_item_count]

    return result_docs


async def handle_conditional_query(
    query_content_type: str | None,
    query_title: str | None,
    query_description: str | None,
    query_date_from: datetime.date | None,
    query_date_to: datetime.date | None,
    max_item_count: int = MAX_ITEM_COUNT,
) -> list[Document]:

    result_group = []

    # Exact filters
    files = file_repository.query_all_files()
    file_tags_map = {
        file.id: tag_repository.get_tags_by_ids(file.tag_ids) for file in files
    }
    docs = [Document.from_file(file, file_tags_map[file.id]) for file in files]
    docs: list[Document] = [doc for doc in docs if doc is not None]
    if query_content_type:
        content_type_query_result_ids_with_scores = [
            (doc, (1 if doc.content_type == query_content_type else 0)) for doc in docs
        ]
        result_group.append(content_type_query_result_ids_with_scores)
    if query_date_from:
        date_from_query_result_ids_with_scores = [
            (doc, (1 if doc.created_at >= query_date_from else 0)) for doc in docs
        ]
        result_group.append(date_from_query_result_ids_with_scores)
    if query_date_to:
        date_to_query_result_ids_with_scores = [
            (doc, (1 if doc.created_at <= query_date_to else 0)) for doc in docs
        ]
        result_group.append(date_to_query_result_ids_with_scores)

    # Fuzzy filters
    if query_title:
        title_query_result_ids_with_scores = (
            await semantic_query_executor.execute_semantic_query(
                query_type="title",
                query_text=query_title,
            )
        )
        result_group.append(title_query_result_ids_with_scores)
    if query_description:
        description_query_result_ids_with_scores = (
            await semantic_query_executor.execute_semantic_query(
                query_type="description",
                query_text=query_description,
            )
        )
        result_group.append(description_query_result_ids_with_scores)

    # Assemble and sort results by score
    result_docs_with_scores = assemble_and_sort_query_results(*result_group)

    # Cut off results
    result_docs = cutoff_results(result_docs_with_scores)[:max_item_count]

    return result_docs
