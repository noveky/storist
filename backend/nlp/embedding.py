import openai, numpy as np, dotenv, os
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity


dotenv.load_dotenv()

client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL"),
)


async def get_embeddings(
    input: list[str], model: str = "text-embedding-3-large"
) -> list[np.ndarray]:
    response = await client.embeddings.create(model=model, input=input)
    return list(np.array(data.embedding) for data in response.data)


def cosine_similarity(vec_1: np.ndarray, vec_2: np.ndarray) -> float:
    return float(
        np.clip(
            sk_cosine_similarity(vec_1.reshape(1, -1), vec_2.reshape(1, -1))[0][0],
            0.0,
            1.0,
        )
    )
