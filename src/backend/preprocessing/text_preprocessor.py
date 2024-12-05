from utils import utils
from backend.llm_prompts import llm_prompts
from backend.nlp import completion_handler

MODEL = "gpt-4o"


async def preprocess_text(text: str, lang: str = "") -> dict | None:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.TEXT_PREPROCESSOR_SYSTEM_PROMPT
    )
    user_prompt = f"""```{lang}\n{text.strip()}\n```"""

    async def try_func():
        nonlocal data
        response = await completion_handler.request_completion(
            model=MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_retries=1,
        )
        _, data = utils.extract_json(response)
        # TODO Verify data validity

    data = None
    try:
        await utils.try_loop_async(try_func, max_retries=3)
        return {"texts": [text], "description": data["描述"]}
    except:
        return None


async def preprocess_text_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return await preprocess_text(text=text, lang=path.split(".")[-1])
