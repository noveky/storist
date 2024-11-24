from utils import utils
from backend import llm_prompts
from backend.nlp import completion_handler

MODEL = "gpt-4o"


async def preprocess_text(text: str, lang: str = "") -> dict:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.TEXT_PREPROCESSOR_SYSTEM_PROMPT
    )
    user_prompt = f"""```{lang}\n{text.strip()}\n```"""
    response = await completion_handler.request_completion(
        model=MODEL,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    _, data = utils.extract_json(response)
    return data["image"]


async def preprocess_text_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return await preprocess_text(text=text, lang=path.split(".")[-1])
