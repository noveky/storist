from . import image_preprocessor, text_preprocessor

from utils import utils
from backend.nlp import embedding_handler

import os


async def preprocess_file(path: str) -> dict:
    print(f"Start preprocessing file: {path}")

    metadata = {}

    file_name = os.path.basename(path)
    file_ext = file_name[file_name.rfind(".") + 1 :]
    metadata["title"] = file_name[: file_name.rfind(".")]
    metadata["file_extension"] = file_ext
    if file_ext in ["jpg", "jpeg", "png"]:
        metadata["type"] = "image"
        result = await image_preprocessor.preprocess_image_file(path)
    elif file_ext in ["txt", "md"]:
        metadata["type"] = "text"
        result = await text_preprocessor.preprocess_text_file(path)
    else:
        result = None  # Not supported, ignore

    if result:
        metadata.update(result)

        description = result.get("description", None)
        if description:
            print(f"Start embedding description for file: {path}")

            async def try_func():
                return await embedding_handler.get_text_embeddings(
                    input_list=[description]
                )[0]

            description_embedding = await utils.try_loop_async(
                try_func, raise_exception=False
            )
            if description_embedding:
                metadata["description_embedding"] = description_embedding

    return metadata
