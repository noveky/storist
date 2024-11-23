from .. import llm_prompts, utils
from ..nlp import completion

MODEL = "gpt-4o"


async def _preprocess_image(image_path: str) -> dict:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.IMAGE_PREPROCESSOR_SYSTEM_PROMPT
    )
    user_prompt = [
        {"type": "text", "text": system_prompt},
        {
            "type": "image_url",
            "image_url": {"url": utils.encode_image_to_base64_data_uri(image_path)},
        },
    ]
    response = await completion.request_completion(
        model=MODEL,
        system_prompt=None,
        user_prompt=user_prompt,
    )
    _, data = utils.extract_yaml(response)
    return data["image"]


async def preprocess_image(image_path: str) -> dict:
    system_prompt = llm_prompts.format_prompt(
        llm_prompts.IMAGE_PREPROCESSOR_SYSTEM_PROMPT_JSON
    )
    user_prompt = [
        {"type": "text", "text": system_prompt},
        {
            "type": "image_url",
            "image_url": {"url": utils.encode_image_to_base64_data_uri(image_path)},
        },
    ]
    response = await completion.request_completion(
        model=MODEL,
        system_prompt=None,
        user_prompt=user_prompt,
    )
    _, data = utils.extract_json(response)
    return data["image"]
