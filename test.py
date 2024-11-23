from backend import utils
from backend.nlp import embedding

import asyncio


async def main():
    src = "这个苹果的颜色是绿色，味道酸甜，采摘自河北省。"
    queries = [
        "苹果",
        "绿色的水果",
        "绿色的甘蔗",
        "红色的水果",
        "来自河北省的水果",
        "来自陕西省的、红色的、苦味的水果",
        "来自河南省的、红色的、苦味的水果",
        "来自海南省的、红色的、苦味的水果",
        "来自安大略省的、红色的、苦味的水果",
        "我到河北省来",
        "酸甜的苹果",
        "酸甜的河北苹果",
        "酸甜的河北青苹果",
        "酸甜的湖北青苹果",
        "味道酸甜、颜色是绿色",
        "味道酸甜",
        "味道酸",
        "颜色是绿色",
        "味道寡淡",
        "颜色是黑色",
    ]
    src, queries = "类别", [
        "种类",
        "分类",
        "类目",
        "category",
        "tag",
        "标签",
        "楼层",
        "阵营",
    ]
    embeddings = await embedding.get_embeddings([src] + queries)
    src_embedding = embeddings[0]
    query_embeddings = embeddings[1:]
    for i, query in enumerate(queries):
        print(f"Similarity between {repr(src)} and {repr(query)}: ", end="")
        similarity = embedding.cosine_similarity(src_embedding, query_embeddings[i])
        print(similarity)


if __name__ == "__main__":
    asyncio.run(main())
