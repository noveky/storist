from .. import utils

import openai, openai_streaming, typing, dotenv, os
from openai.types.chat import ChatCompletionMessage

PRINT_STREAM_RESPONSE = True


dotenv.load_dotenv()

client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL"),
)


async def content_handler(content: typing.AsyncGenerator[str, None]):
    if not PRINT_STREAM_RESPONSE:
        return
    async for token in content:
        print(token, end="", flush=True)
    print()


async def request_completion(
    model: str,
    system_prompt: str | None,
    user_prompt: str | list,
    temperature: float | None = None,
    max_tokens: int = 8192,
) -> tuple[set[str], ChatCompletionMessage]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append(
        {
            "role": "user",
            "content": (
                user_prompt.strip() if isinstance(user_prompt, str) else user_prompt
            ),
        }
    )

    async def try_func():
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=temperature or 0.0,
            max_tokens=max_tokens,
        )
        response = await openai_streaming.process_response(
            response=response,
            content_func=content_handler,
        )
        return response[1].content

    return await utils.try_loop_async(try_func)
