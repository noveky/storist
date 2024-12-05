from utils import utils
from backend.llm_prompts import llm_prompts
from backend.nlp import completion_handler

MODEL = "gpt-4o"


async def preprocess_image(image_base64: str) -> dict:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.IMAGE_PREPROCESSOR_SYSTEM_PROMPT
    )
    user_prompt = [
        {"type": "text", "text": system_prompt},
        {
            "type": "image_url",
            "image_url": {"url": image_base64},
        },
    ]

    async def try_func():
        nonlocal data
        response = await completion_handler.request_completion(
            model=MODEL,
            system_prompt=None,
            user_prompt=user_prompt,
            max_retries=1,
        )
        _, data = utils.extract_json(response)
        # TODO Verify data validity

    data = None
    try:
        await utils.try_loop_async(try_func, max_retries=3)
        return {"texts": data["文本"], "description": data["描述"]}
    except:
        return None


async def preprocess_image_file(path: str) -> dict:
    image_base64 = utils.encode_image_to_base64_data_uri(path)
    return await preprocess_image(image_base64)
