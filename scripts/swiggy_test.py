import asyncio

from app.models.grocery import GroceryItem
from app.services.swiggy.address import select_address
from app.services.swiggy.grocery_flow import find_matches
from app.services.swiggy.selection import select_product


async def main():
    grocery_item = GroceryItem(
        name="potato",
        quantity=1,
        unit="kg",
        original_text="potato 1kg",
        confidence=1.0,
    )

    address = await select_address()

    print(f"\nSearching for: {grocery_item.original_text}\n")

    ranked_products = await find_matches(
        grocery_item=grocery_item,
        address_id=address.id,
    )

    selected_product = select_product(ranked_products)

    if selected_product is None:
        print("\nNo product selected.")
        return

    print("\nPRODUCT SELECTED")
    print("=" * 70)
    print(f"Product: {selected_product.product.display_name}")
    print(f"Match: {selected_product.match}")
    print(f"Confidence: {selected_product.confidence:.2f}")
    print(f"Reason: {selected_product.reason}")

    print("\nNo cart changes were made.")


if __name__ == "__main__":
    asyncio.run(main())