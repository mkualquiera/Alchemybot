from typing import Any, List, Optional
import openai
from openai.types.chat import (
    ChatCompletionMessageParam,
)
import os
import json

client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


async def get_json_data(
    system_prompt: str,
    user_prompt: Optional[str] = None,
    image_url: Optional[str] = None,
    model="gpt-4",
) -> Any:
    if image_url is not None and model != "gpt-4-vision-preview":
        raise Exception("Image url provided but model is not gpt-4-vision-preview")

    print("Getting json data...", end="", flush=True)
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
    ]
    if user_prompt is not None:
        if image_url is None:
            messages.append({"role": "user", "content": user_prompt})
        else:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }  # type: ignore
            )
    chat_completion = await client.chat.completions.create(
        messages=messages, model=model, max_tokens=1000
    )

    result = chat_completion.choices[0].message.content

    if result is None:
        raise Exception("Empty assistant message on get json data")

    # Unicode checkmark when done
    print("✅")

    print(result)

    result = json.loads(result)

    return result


async def get_embedding(text: str) -> List[float]:
    """Returns a list of floats representing the embedding of the text."""
    print("Getting embedding...", end="", flush=True)
    embedding = await client.embeddings.create(
        input=[text], model="text-embedding-ada-002"
    )
    print("✅")
    return embedding.data[0].embedding
