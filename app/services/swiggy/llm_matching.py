import json

import httpx

from app.core.config import settings
from app.models.grocery import GroceryItem
# from app.models.swiggy import ProductCandidate

from app.models.swiggy import (
    ProductCandidate,
    ProductMatchingResult,
)

MATCHING_SYSTEM_PROMPT = """
You are a grocery product matching assistant.

Your job is to match a user's requested grocery item against products
returned by a grocery delivery service.

Consider:

1. Product identity
   - Is this actually the requested grocery item?
   - Do not treat a combo containing the requested item as an exact match.

2. Quantity

   - Compare the requested quantity with the available variation.
   - Understand equivalent quantities such as:
     1 kg = 1000 g
     500 g x 2 = 1 kg

   - NEVER infer, estimate, or assume a quantity that is not explicitly
     present in the product data.

   - If the requested quantity is 1 kg and the product only says
     "1 Pack" without specifying its weight, do NOT assume that the pack
     contains 1 kg.

   - An unspecified quantity should reduce confidence.

   - A quantity mismatch should normally result in "poor" rather than
     "acceptable".

3. Product variants

   - A different variety may be an acceptable alternative but should not
     automatically be considered an exact match.
   - Example: "potato" and "baby potato" are not necessarily identical.
   - If the requested item is generic, a specific variety can be an
     acceptable alternative when the quantity matches.

4. Combos
   - A product such as "Onion & Potato" is not an exact match for "potato".

5. Availability
   - Prefer products and variations that are currently available.

6. Sponsored products
   - Do not increase a product's match quality merely because it is promoted.

7. Evidence constraint

   Base every classification only on information explicitly provided
   in the requested item and candidate data.

   Do not use outside knowledge to fill missing product information.

   If important information is missing, lower the confidence or classify
   the candidate as "poor" or "reject" rather than guessing.

For every candidate, classify the match as one of:

- "exact"
- "acceptable"
- "poor"
- "reject"

Return a confidence between 0 and 1.

The confidence represents how confident you are in the classification,
not the probability that the user will purchase it.

For every candidate, also provide a short reason explaining the
classification.

Return JSON only in this format:

{
  "matches": [
    {
      "product_index": 0,
      "variation_index": 0,
      "match": "exact",
      "confidence": 0.95,
      "reason": "..."
    }
  ]
}
"""


async def match_products(
    grocery_item: GroceryItem,
    products: list[ProductCandidate],
) -> ProductMatchingResult:
    candidates = []

    for product_index, product in enumerate(products):
        for variation_index, variation in enumerate(product.variations):
            candidates.append(
                {
                    "product_index": product_index,
                    "variation_index": variation_index,
                    "product": {
                        "name": product.display_name,
                        "brand": product.brand,
                        "is_promoted": product.is_promoted,
                    },
                    "variation": {
                        "quantity": variation.quantity_description,
                        "available": variation.is_in_stock_and_available,
                        "price": (
                            variation.price.offer_price
                            if variation.price
                            else None
                        ),
                    },
                }
            )

    user_prompt = {
        "requested_item": {
            "name": grocery_item.name,
            "quantity": grocery_item.quantity,
            "unit": grocery_item.unit,
            "original_text": grocery_item.original_text,
        },
        "candidates": candidates,
    }

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "system",
                "content": MATCHING_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_prompt,
                    ensure_ascii=False,
                ),
            },
        ],
        "response_format": {
            "type": "json_object",
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

    return ProductMatchingResult.model_validate(parsed)