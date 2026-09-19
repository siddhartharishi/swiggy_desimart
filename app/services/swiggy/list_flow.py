from app.models.grocery import GroceryItem, GroceryList
from app.services.swiggy.grocery_flow import find_matches
from app.services.swiggy.ranking import RankedProduct
from app.services.swiggy.selection import select_product


async def process_grocery_item(
    grocery_item: GroceryItem,
    address_id: str,
) -> RankedProduct | None:
    """
    Find and let the user select a product for one grocery item.
    """

    print("\n" + "=" * 70)
    print(f"ITEM: {grocery_item.original_text}")
    print("=" * 70)

    ranked_products = await find_matches(
        grocery_item=grocery_item,
        address_id=address_id,
    )

    if not ranked_products:
        print("No matching products found.")
        return None

    return select_product(ranked_products)


async def process_grocery_list(
    grocery_list: GroceryList,
    address_id: str,
) -> list[tuple[GroceryItem, RankedProduct]]:
    """
    Process every grocery item and collect the user's selections.
    """

    selections = []

    for grocery_item in grocery_list.items:
        selected_product = await process_grocery_item(
            grocery_item=grocery_item,
            address_id=address_id,
        )

        if selected_product is not None:
            selections.append(
                (grocery_item, selected_product)
            )

    return selections