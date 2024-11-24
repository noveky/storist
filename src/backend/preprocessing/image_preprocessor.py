from utils import utils
from backend import llm_prompts
from backend.nlp import completion

MODEL = "gpt-4o"


async def preprocess_image(image_base64: str):
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
    response = await completion.request_completion(
        model=MODEL,
        system_prompt=None,
        user_prompt=user_prompt,
    )
    _, data = utils.extract_json(response)
    return data["image"]


async def preprocess_image_file(path: str):
    print(f"Start preprocessing image file {path}")
    image_base64 = utils.encode_image_to_base64_data_uri(path)
    return await preprocess_image(image_base64)
