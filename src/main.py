from backend import utils
from backend.preprocessing import image_preprocessor
from backend.query import query_handler
from backend.fs import file_system_watcher

import asyncio
from sklearn.metrics.pairwise import cosine_similarity


async def main():
    print(await image_preprocessor.preprocess_image("data/test.png"))
    query = input("Query: ")
    result_items = await query_handler.handle_query(query)
    print(result_items)


if __name__ == "__main__":
    asyncio.run(main())
