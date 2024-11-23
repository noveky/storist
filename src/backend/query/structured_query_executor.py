from backend.db import database
from backend.db.models import *
from backend.nlp import embedding
from .psql_ast import *

import math


async def execute_graph_query(query: SelectStmt):

    def transform_expr(expr, is_condition_expr: bool) -> typing.Any:
        if isinstance(expr, Identifier):
            if is_condition_expr:
                return Operation("=", expr, Value(True))
        elif isinstance(expr, FunctionCall):
            raise NotImplementedError()
        elif isinstance(expr, Operation):
            if all(isinstance(operand, Value) for operand in expr.operands):
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
            else:
                for i, operand in enumerate(expr.operands):
                    expr.operands[i] = transform_expr(operand, is_condition_expr=True)
                # TODO Ensure the first operand is attribute
        return expr

    query.condition = transform_expr(query.condition, is_condition_expr=True)

    def collect_query_attributes(expr):
        nonlocal texts_to_embed

        if isinstance(expr, Identifier):
            texts_to_embed.add(expr.name)
        elif isinstance(expr, FunctionCall):
            for arg in expr.arguments:
                collect_query_attributes(arg)
        elif isinstance(expr, Operation):
            for operand in expr.operands:
                collect_query_attributes(operand)

    texts_to_embed = set[str]()
    collect_query_attributes(query.condition)

    texts_to_embed = list(texts_to_embed)
    text_vector_map = {
        text: vector
        for text, vector in zip(
            texts_to_embed, await embedding.get_embeddings(texts_to_embed)
        )
    }

    # Retrieve all triples
    triples = database.retrieve_triples()

    # Populate item_ids and item_triples_map
    item_ids = set()
    item_triples_map: dict[int, list[Triple]] = {}
    async for triple in triples:
        item_ids.add(triple.item_id)
        if triple.item_id not in item_triples_map:
            item_triples_map[triple.item_id] = []
        item_triples_map[triple.item_id].append(triple)

    item_score_map = {}

    for item_id in item_ids:
        item_triples = item_triples_map[item_id]

        def compute_score(expr) -> float:
            nonlocal item_triples, text_vector_map

            if isinstance(expr, Value):
                return 1 if bool(expr.value) else 0
            elif isinstance(expr, Operation):
                if expr.operator == "OR":
                    return max(compute_score(operand) for operand in expr.operands)
                elif expr.operator == "AND":
                    return math.prod(
                        compute_score(operand) for operand in expr.operands
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
                        score = 0
                        for triple in item_triples:
                            attr_score = embedding.cosine_similarity(
                                text_vector_map[query_attr],
                                triple.attr_embedding_vector,
                            )
                            if expr.operator in ("=", "<>") and isinstance(
                                expr.operands[1], Value
                            ):
                                query_value = expr.operands[1].value
                                value_score = (
                                    embedding.cosine_similarity(
                                        text_vector_map[query_value],
                                        triple.value_embedding_vector,
                                    )
                                    if isinstance(query_value, str)
                                    or isinstance(triple.value, str)
                                    else (1 if query_value == triple.value else 0)
                                )
                                if expr.operator == "<>":
                                    value_score = 1 - value_score
                                score = np.clip(score, 0, 1)
                            elif all(
                                isinstance(operand, Value)
                                and isinstance(
                                    operand.value, int | float | datetime.date
                                )
                                for operand in expr.operands[1:]
                            ):
                                if expr.operator == "<":
                                    value_score = (
                                        1
                                        if triple.value < expr.operands[1].value
                                        else 0
                                    )
                                elif expr.operator == "<=":
                                    value_score = (
                                        1
                                        if triple.value <= expr.operands[1].value
                                        else 0
                                    )
                                elif expr.operator == ">":
                                    value_score = (
                                        1
                                        if triple.value > expr.operands[1].value
                                        else 0
                                    )
                                elif expr.operator == ">=":
                                    value_score = (
                                        1
                                        if triple.value >= expr.operands[1].value
                                        else 0
                                    )
                                elif expr.operator == "BETWEEN":
                                    value_score = (
                                        1
                                        if triple.value >= expr.operands[1].value
                                        and triple.value <= expr.operands[2].value
                                        else 0
                                    )
                            else:
                                raise NotImplementedError()  # TODO
                            score += attr_score * value_score
                        return score
            raise NotImplementedError()

        score = compute_score(query.condition)
        item_score_map[item_id] = score

    # Zip the item ids with their corresponding scores
    item_ids_with_scores = [(sid, item_score_map[sid]) for sid in item_ids]

    return item_ids_with_scores
