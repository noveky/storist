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
    metadata["created_at"] = os.path.getctime(path)
    if file_ext in ["jpg", "jpeg", "png", "bmp", "gif"]:
        metadata["content_type"] = "image"
        preprocessor_result = await image_preprocessor.preprocess_image_file(path)
    elif file_ext in ["txt", "md"]:
        metadata["content_type"] = "text"
        preprocessor_result = await text_preprocessor.preprocess_text_file(path)
    else:
        # Not supported
        metadata["content_type"] = None
        preprocessor_result = None

    if preprocessor_result is None:
        return metadata

    metadata.update(preprocessor_result)

    async def try_func():
        return await embedding_handler.get_text_embeddings(
            input_list=[title, description]
        )

    print(f"Start embedding title and description for file: {path}")
    title = metadata["title"]
    description = metadata["description"]
    embeddings = await utils.try_loop_async(try_func, raise_exception=False)
    if embeddings is None:
        return metadata

    print(f"Finished embedding title and description for file: {path}")
    title_embedding, description_embedding = embeddings
    metadata["title_embedding"] = list(title_embedding)
    metadata["description_embedding"] = list(description_embedding)

    print(f"Preprocessing done for file: {path}")
    metadata["preprocessing_done"] = True
    return metadata
