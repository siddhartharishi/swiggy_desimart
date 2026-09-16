import re
from dataclasses import dataclass

from app.models.grocery import GroceryItem
from app.models.swiggy import ProductCandidate, ProductVariation


@dataclass
class RankedVariation:
    product: ProductCandidate
    variation: ProductVariation
    score: float


def normalize_text(text: str) -> str:
    """
    Normalize text for matching.
    """

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return " ".join(text.split())


def product_name_score(
    grocery_item: GroceryItem,
    product: ProductCandidate,
) -> float:
    """
    Score how well the Swiggy product name matches
    the requested grocery item.
    """

    grocery_name = normalize_text(
        grocery_item.name
    )

    product_name = normalize_text(
        product.display_name
    )

    if grocery_name == product_name:
        return 1.0

    product_words = set(
        product_name.split()
    )

    grocery_words = set(
        grocery_name.split()
    )

    if grocery_words.issubset(product_words):
        return 0.8

    return 0.0


def combo_penalty(
    product: ProductCandidate,
) -> float:
    """
    Penalize products that contain multiple grocery
    items such as 'Onion, Potato & Tomato'.
    """

    product_name = normalize_text(
        product.display_name
    )

    combo_indicators = [
        "combo",
        "onion potato",
        "potato tomato",
        "onion tomato",
        "&",
    ]

    for indicator in combo_indicators:
        if indicator in product_name:
            return 0.3

    return 0.0


def variation_score(
    grocery_item: GroceryItem,
    variation: ProductVariation,
) -> float:
    """
    Score how well a variation matches the requested
    quantity and unit.
    """

    if (
        grocery_item.quantity is None
        or grocery_item.unit is None
    ):
        return 0.5

    if not variation.quantity_description:
        return 0.0

    quantity_text = normalize_text(
        variation.quantity_description
    )

    requested_quantity = str(
        grocery_item.quantity
    )

    requested_unit = normalize_text(
        grocery_item.unit
    )

    if (
        requested_quantity in quantity_text
        and requested_unit in quantity_text
    ):
        return 1.0

    return 0.0


def score_product(
    grocery_item: GroceryItem,
    product: ProductCandidate,
    variation: ProductVariation,
) -> float:
    """
    Calculate the final candidate score.
    """

    name_score = product_name_score(
        grocery_item,
        product,
    )

    quantity_score = variation_score(
        grocery_item,
        variation,
    )

    penalty = combo_penalty(product)

    score = (
        0.6 * name_score
        + 0.4 * quantity_score
        - penalty
    )

    return max(
        0.0,
        min(1.0, score),
    )


def rank_product_variations(
    grocery_item: GroceryItem,
    products: list[ProductCandidate],
) -> list[RankedVariation]:
    """
    Rank all available product variations.
    """

    ranked: list[RankedVariation] = []

    for product in products:

        for variation in product.variations:

            if not variation.is_in_stock_and_available:
                continue

            score = score_product(
                grocery_item=grocery_item,
                product=product,
                variation=variation,
            )

            ranked.append(
                RankedVariation(
                    product=product,
                    variation=variation,
                    score=score,
                )
            )

    ranked.sort(
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    return ranked