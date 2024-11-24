from . import image_preprocessor, text_preprocessor


async def preprocess_file(path: str):
    if path.endswith(".png") or path.endswith(".jpg") or path.endswith(".jpeg"):
        return await image_preprocessor.preprocess_image_file(path)
    elif path.endswith(".txt") or path.endswith(".md"):
        return await text_preprocessor.preprocess_text_file(path)
    else:
        pass  # Not supported, ignore
