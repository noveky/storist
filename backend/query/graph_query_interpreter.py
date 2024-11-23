from . import sql_parser
from ..nlp import completion
from .. import llm_prompts, utils

MODEL = "gpt-4o-mini"


def extract_and_parse_sql(text: str):
    sql_codes = [
        sql_code for _, sql_code in utils.extract_code_blocks(text, target_cls="sql")
    ]

    if len(sql_codes) != 1:
        raise ValueError("Expected exactly one SQL code block in the text")

    sql_code = str(sql_codes[0]).strip()
    return sql_parser.parse(sql_code)


async def interpret_query(query: str) -> sql_parser.SelectStmt:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.QUERY_INTERPRETER_SYSTEM_PROMPT
    )
    user_prompt = f"""```\n{query.strip()}\n```"""

    async def try_func():
        nonlocal sql_parse_tree

        response = await completion.request_completion(
            model=MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        sql_parse_tree = extract_and_parse_sql(response)
        if sql_parse_tree.from_table_name != "db":
            raise ValueError("Invalid response")

    sql_parse_tree: sql_parser.SelectStmt = None
    await utils.try_loop_async(try_func)

    return sql_parse_tree
