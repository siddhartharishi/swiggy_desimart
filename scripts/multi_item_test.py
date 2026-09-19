import asyncio

from app.models.grocery import GroceryItem, GroceryList
from app.services.swiggy.address import select_address
from app.services.swiggy.list_flow import process_grocery_list


async def main():
    grocery_list = GroceryList(
        items=[
            GroceryItem(
                name="potato",
                quantity=1,
                unit="kg",
                original_text="potato 1kg",
                confidence=0.95,
            ),
            GroceryItem(
                name="milk",
                quantity=2,
                unit="packets",
                original_text="milk 2 packets",
                confidence=0.96,
            ),
            GroceryItem(
                name="rice",
                quantity=5,
                unit="kg",
                original_text="rice 5kg",
                confidence=0.94,
            ),
        ]
    )

    address = await select_address()

    selections = await process_grocery_list(
        grocery_list=grocery_list,
        address_id=address.id,
    )

    print("\n" + "=" * 70)
    print("FINAL SELECTIONS")
    print("=" * 70)

    for grocery_item, selected_product in selections:
        variation = selected_product.product.variations[
            selected_product.variation_index
        ]

        print(f"\nRequested: {grocery_item.original_text}")
        print(f"Selected: {selected_product.product.display_name}")
        print(f"Quantity: {variation.quantity_description}")
        print(f"Match: {selected_product.match}")
        print(f"Confidence: {selected_product.confidence:.2f}")

    print("\nNo cart changes were made.")


if __name__ == "__main__":
    asyncio.run(main())