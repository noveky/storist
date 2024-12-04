from backend.models.models import *
from backend.repositories import file_repository, tag_repository
from backend.nlp import embedding_handler

import typing


async def execute_semantic_query(
    query_text: str, query_type: typing.Literal["title", "description"]
):
    # Embed the query
    query_vector = (await embedding_handler.get_text_embeddings([query_text]))[0]

    # Retrieve all documents
    files = file_repository.query_all_files()
    file_tags_map = {
        file.id: [tag_repository.get_tag_by_id(tag_id) for tag_id in file.tag_ids]
        for file in files
    }
    docs = [Document.from_file(file, file_tags_map[file.id]) for file in files]
    docs: list[Document] = [doc for doc in docs if doc is not None]

    # Compute the score for each document
    doc_scores = {}  # {doc: score}
    for i, doc in enumerate(docs):
        doc_scores[i] = embedding_handler.cosine_similarity(
            query_vector,
            np.array(
                doc.file.metadata[
                    (
                        "title_embedding"
                        if query_type == "title"
                        else "description_embedding"
                    )
                ]
            ),
        )

    # Zip the documents with their corresponding scores
    docs_with_scores = [(doc, doc_scores[i]) for i, doc in enumerate(docs)]

    return docs_with_scores
