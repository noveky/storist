from . import image_preprocessor, text_preprocessor

from utils import utils
from backend.nlp import embedding_handler

import os, datetime


async def preprocess_file(path: str) -> dict:
    print(f"Start preprocessing file: {path}")

    metadata = {}

    file_name = os.path.basename(path)
    file_ext = file_name[file_name.rfind(".") + 1 :]
    metadata["title"] = file_name[: file_name.rfind(".")]
    metadata["file_extension"] = file_ext
    metadata["datetime_created"] = datetime.datetime.fromtimestamp(
        os.path.getctime(path)
    ).isoformat()
    if file_ext in ["jpg", "jpeg", "png"]:
        metadata["content_type"] = "image"
        preprocessor_result = await image_preprocessor.preprocess_image_file(path)
    elif file_ext in ["txt", "md"]:
        metadata["content_type"] = "text"
        preprocessor_result = await text_preprocessor.preprocess_text_file(path)
    else:
        metadata["content_type"] = None
        preprocessor_result = None  # Not supported

    if preprocessor_result:
        metadata.update(preprocessor_result)

        title = metadata["title"]
        description = metadata["description"]

        print(f"Start embedding title and description for file: {path}")

        async def try_func():
            return await embedding_handler.get_text_embeddings(
                input_list=[title, description]
            )

        title_embedding, description_embedding = await utils.try_loop_async(
            try_func, raise_exception=False
        )
        if title_embedding:
            metadata["title_embedding"] = title_embedding
        if description_embedding:
            metadata["description_embedding"] = description_embedding

    return metadata
