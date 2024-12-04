from backend.repositories import file_repository, tag_repository
from backend.models.models import *
from backend.nlp import embedding_handler
from .ssql_ast import *


async def execute_structured_query(query: SelectStmt):
    print(query)

    def transform_expr(expr, is_condition_expr: bool) -> typing.Any:
        if isinstance(expr, Identifier):
            if is_condition_expr:
                return Operation(
                    "=", expr, Value(True)
                )  # Transform to explicit comparison with TRUE
        elif isinstance(expr, FunctionCall):
            raise NotImplementedError()
        elif isinstance(expr, Operation):
            if all(
                operand.name in ("title", "description")
                for operand in expr.operands
                if isinstance(operand, Identifier)
            ):
                if expr.operator in ("LIKE", "NOT LIKE", "=", "<>"):
                    return Operation(
                        "SLIKE" if expr.operator in ("LIKE", "=") else "NSLIKE",
                        *expr.operands
                    )
            elif all(isinstance(operand, Value) for operand in expr.operands):
                if expr.operator == "OR":
                    return Value(any(operand.value for operand in expr.operands))
                elif expr.operator == "AND":
                    return Value(all(operand.value for operand in expr.operands))
                elif expr.operator == "NOT":
                    return Value(not expr.operands[0].value)
                elif expr.operator == "=":
                    return Value(expr.operands[0].value == expr.operands[1].value)
                elif expr.operator == "<>":
                    return Value(expr.operands[0].value != expr.operands[1].value)
                elif expr.operator == "<":
                    return Value(expr.operands[0].value < expr.operands[1].value)
                elif expr.operator == "<=":
                    return Value(expr.operands[0].value <= expr.operands[1].value)
                elif expr.operator == ">":
                    return Value(expr.operands[0].value > expr.operands[1].value)
                elif expr.operator == ">=":
                    return Value(expr.operands[0].value >= expr.operands[1].value)
                elif expr.operator == "BETWEEN":
                    return Value(
                        expr.operands[0].value >= expr.operands[1].value
                        and expr.operands[1].value <= expr.operands[2].value
                    )
            elif expr.operator in ("OR", "AND"):
                for i, operand in enumerate(expr.operands):
                    expr.operands[i] = transform_expr(operand, is_condition_expr=True)
        return expr

    query.condition = transform_expr(query.condition, is_condition_expr=True)

    def collect_query_attributes(expr):
        nonlocal texts_to_embed

        if isinstance(expr, FunctionCall):
            for arg in expr.arguments:
                collect_query_attributes(arg)
        elif isinstance(expr, Operation):
            if expr.operator in ("LIKE", "NOT LIKE", "=", "<>"):
                for operand in expr.operands:
                    if isinstance(operand, Value) and isinstance(operand.value, str):
                        texts_to_embed.add(operand.value)
            for operand in expr.operands:
                collect_query_attributes(operand)

    texts_to_embed = set[str]()
    collect_query_attributes(query.condition)

    texts_to_embed = list(texts_to_embed)
    texts_to_embed_clean = [text.replace("%", "") for text in texts_to_embed]
    texts_to_embed_clean = [
        " " if text == "" else text for text in texts_to_embed_clean
    ]
    text_vector_map = {
        text: vector
        for text, vector in zip(
            texts_to_embed,
            await embedding_handler.get_text_embeddings(texts_to_embed_clean),
        )
    }

    # Retrieve all documents
    files = file_repository.query_all_files()
    file_tags_map = {
        file.id: [tag_repository.get_tag_by_id(tag_id) for tag_id in file.tag_ids]
        for file in files
    }
    docs = [Document.from_file(file, file_tags_map[file.id]) for file in files]
    docs: list[Document] = [doc for doc in docs if doc is not None]

    doc_scores = {}  # {doc: score}

    for i, doc in enumerate(docs):

        def compute_score(expr) -> float:
            nonlocal text_vector_map

            if isinstance(expr, Value):
                return 1 if bool(expr.value) else 0
            elif isinstance(expr, Operation):
                if expr.operator == "OR":
                    return np.mean(
                        [compute_score(operand) for operand in expr.operands]
                    )
                elif expr.operator == "AND":
                    return np.prod(
                        [compute_score(operand) for operand in expr.operands]
                    )
                elif expr.operator == "NOT":
                    return 1 - compute_score(expr.operands[0])
                elif expr.operator in (
                    "=",
                    "<>",
                    "<",
                    "<=",
                    ">",
                    ">=",
                    "BETWEEN",
                ):
                    if isinstance(expr.operands[0], Identifier):
                        query_attr = expr.operands[0].name
                        if query_attr == "content_type":
                            attr_value = doc.content_type
                        elif query_attr in ("title", "description"):
                            attr_value = np.array(
                                doc.file.metadata[
                                    (
                                        "title_embedding"
                                        if query_attr == "title"
                                        else "description_embedding"
                                    )
                                ]
                            )
                        elif query_attr == "created_at":
                            attr_value = datetime.date.fromtimestamp(
                                doc.created_at.timestamp()
                            )
                        if expr.operator in ("SLIKE", "NSLIKE"):
                            assert query_attr in ("title", "description")
                            if isinstance(expr.operands[1], Value):
                                query_value = text_vector_map[query_value]
                            elif isinstance(expr.operands[1], Identifier):
                                query_attr_right = expr.operands[1].name
                                assert query_attr_right in ("title", "description")
                                query_value = np.array(
                                    doc.file.metadata[
                                        (
                                            "title_embedding"
                                            if query_attr_right == "title"
                                            else "description_embedding"
                                        )
                                    ]
                                )
                            elif isinstance(expr.operands[1], FunctionCall):
                                raise NotImplementedError()  # TODO
                            else:
                                raise RuntimeError("Invalid operand type")
                            score = embedding_handler.cosine_similarity(
                                query_value, attr_value
                            )
                            if expr.operator == "NSLIKE":
                                score = 1 - score
                        elif all(
                            isinstance(operand, Value)
                            and isinstance(operand.value, int | float | datetime.date)
                            for operand in expr.operands[1:]
                        ):
                            if expr.operator == "=":
                                score = 1 if attr_value == expr.operands[1].value else 0
                            elif expr.operator == "<>":
                                score = 1 if attr_value != expr.operands[1].value else 0
                            elif expr.operator == "<":
                                score = 1 if attr_value < expr.operands[1].value else 0
                            elif expr.operator == "<=":
                                score = 1 if attr_value <= expr.operands[1].value else 0
                            elif expr.operator == ">":
                                score = 1 if attr_value > expr.operands[1].value else 0
                            elif expr.operator == ">=":
                                score = 1 if attr_value >= expr.operands[1].value else 0
                            elif expr.operator == "BETWEEN":
                                score = (
                                    1
                                    if attr_value >= expr.operands[1].value
                                    and attr_value <= expr.operands[2].value
                                    else 0
                                )
                        else:
                            raise NotImplementedError()  # TODO
                        score = np.clip(score, 0, 1)
                        return score
            return 0
            raise NotImplementedError()

        score = compute_score(query.condition)
        doc_scores[i] = score

    # Zip the documents with their corresponding scores
    docs_with_scores = [(doc, doc_scores[i]) for i, doc in enumerate(docs)]

    return docs_with_scores
