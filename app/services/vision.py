import base64
import json

import httpx

from app.core.config import settings
from app.models.grocery import GroceryList
from app.prompts.grocery_extraction import GROCERY_EXTRACTION_SYSTEM_PROMPT


async def extract_grocery_list(
    image_bytes: bytes,
    content_type: str,
) -> GroceryList:
    """
    Send a grocery-list image to the vision model and return
    a validated GroceryList.
    """

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data_url = f"data:{content_type};base64,{image_base64}"

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "system",
                "content": GROCERY_EXTRACTION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the grocery items from this handwritten list.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "grocery_list",
                "strict": True,
                "schema": GroceryList.model_json_schema(),
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    content = data["choices"][0]["message"]["content"]

    if isinstance(content, list):
        content = "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict)
        )

    parsed = json.loads(content)

    return GroceryList.model_validate(parsed)