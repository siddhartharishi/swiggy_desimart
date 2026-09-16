from app.models.grocery import GroceryItem
from app.models.swiggy import ProductCandidate
from app.services.swiggy.client import search_products, update_cart
from app.services.swiggy.llm_matching import match_products
from app.services.swiggy.ranking import RankedProduct, rank_matches


MAX_CANDIDATES = 10


def prepare_candidates(
    products: list[ProductCandidate],
) -> list[ProductCandidate]:
    """
    Keep only products that have at least one available variation.
    Limit the number of candidates sent to the LLM.
    """

    usable_products = []

    for product in products:
        has_available_variation = any(
            variation.is_in_stock_and_available
            for variation in product.variations
        )

        if not has_available_variation:
            continue

        usable_products.append(product)

    return usable_products[:MAX_CANDIDATES]


async def find_matches(
    grocery_item: GroceryItem,
    address_id: str,
) -> list[RankedProduct]:
    """
    Search Swiggy for a grocery item and rank the returned products.
    """

    search_result = await search_products(
        address_id=address_id,
        query=grocery_item.name,
    )

    # For now, use direct search results only.
    # Similar products can become a fallback later.
    products: list[ProductCandidate] = prepare_candidates(
        search_result.products
    )

    if not products:
        return []

    matching_result = await match_products(
        grocery_item=grocery_item,
        products=products,
    )

    ranked_products = rank_matches(
        products=products,
        matches=matching_result.matches,
    )

    return ranked_products


async def add_to_cart(
    address_id: str,
    ranked_product: RankedProduct,
    quantity: int = 1,
):
    """
    Add a user-approved product variation to the Swiggy cart.
    """

    return await update_cart(
        selected_address_id=address_id,
        spin_id=ranked_product.spin_id,
        quantity=quantity,
    )