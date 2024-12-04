from . import ssql_parser

from utils import utils
from backend.nlp import completion_handler
from backend import llm_prompts

MODEL = "gpt-4o"


def extract_and_parse_sql(text: str):
    sql_codes = [
        sql_code for _, sql_code in utils.extract_code_blocks(text, target_cls="sql")
    ]

    if len(sql_codes) != 1:
        raise ValueError("Expected exactly one SQL code block in the text")

    sql_code = str(sql_codes[0]).strip()
    return ssql_parser.parse(sql_code)


async def interpret_query(query: str) -> ssql_parser.SelectStmt:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.QUERY_INTERPRETER_SYSTEM_PROMPT
    )
    user_prompt = f"""```\n{query.strip()}\n```"""

    async def try_func():
        nonlocal sql_parse_tree

        response = await completion_handler.request_completion(
            model=MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        sql_parse_tree = extract_and_parse_sql(response)
        if sql_parse_tree.from_table_name != "documents":
            raise ValueError("Invalid response")

    sql_parse_tree: ssql_parser.SelectStmt = None
    await utils.try_loop_async(try_func)

    return sql_parse_tree
