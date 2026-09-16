from dataclasses import dataclass

from app.models.swiggy import ProductCandidate, ProductMatch


MATCH_PRIORITY = {
    "exact": 3,
    "acceptable": 2,
    "poor": 1,
    "reject": 0,
}


@dataclass
class RankedProduct:
    product: ProductCandidate
    variation_index: int
    match: str
    confidence: float
    reason: str
    spin_id: str
    sku_id: str


def rank_matches(
    products: list[ProductCandidate],
    matches: list[ProductMatch],
) -> list[RankedProduct]:
    ranked = []

    for match in matches:
        if match.product_index >= len(products):
            continue

        product = products[match.product_index]

        if match.variation_index >= len(product.variations):
            continue

        variation = product.variations[match.variation_index]

        ranked.append(
            RankedProduct(
                product=product,
                variation_index=match.variation_index,
                match=match.match,
                confidence=match.confidence,
                reason=match.reason,
                spin_id=variation.spin_id,
                sku_id=variation.sku_id,
            )
        )

    ranked.sort(
        key=lambda item: (
            MATCH_PRIORITY.get(item.match, 0),
            item.confidence,
        ),
        reverse=True,
    )

    return ranked