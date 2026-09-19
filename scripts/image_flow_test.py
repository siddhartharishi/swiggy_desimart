import asyncio
import sys
from pathlib import Path

from app.services.swiggy.address import select_address
from app.services.swiggy.cart_flow import (
    add_selected_products_to_cart,
    confirm_cart,
    show_cart_plan,
)
from app.services.swiggy.client import get_cart
from app.services.swiggy.list_flow import process_grocery_list
from app.services.vision import extract_grocery_list


async def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m scripts.image_flow_test <image_path>"
        )
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return

    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    content_type = content_type_map.get(
        image_path.suffix.lower()
    )

    if content_type is None:
        print(
            "Unsupported image type. "
            "Use JPG, JPEG, PNG, WEBP, or GIF."
        )
        return

    image_bytes = image_path.read_bytes()

    print("\nReading grocery list from image...")

    grocery_list = await extract_grocery_list(
        image_bytes=image_bytes,
        content_type=content_type,
    )

    if not grocery_list.items:
        print("\nNo grocery items were detected.")
        return

    print("\nEXTRACTED GROCERY LIST")
    print("=" * 70)

    for index, item in enumerate(
        grocery_list.items,
        start=1,
    ):
        print(f"\n{index}. {item.name}")

        if item.quantity is not None:
            print(f"   Quantity: {item.quantity}")

        if item.unit:
            print(f"   Unit: {item.unit}")

        print(f"   Original text: {item.original_text}")
        print(f"   Confidence: {item.confidence:.2f}")

    address = await select_address()

    selections = await process_grocery_list(
        grocery_list=grocery_list,
        address_id=address.id,
    )

    if not selections:
        print("\nNo products were selected.")
        return

    show_cart_plan(selections)

    approved = confirm_cart(selections)

    if not approved:
        print("\nCart operation cancelled.")
        return

    print("\nAdding selected products to cart...")

    results = await add_selected_products_to_cart(
        selections=selections,
        address_id=address.id,
    )

    print("\nProducts added successfully.")

    print("\nVERIFYING CART")
    print("=" * 70)

    cart = await get_cart()

    print(cart)


if __name__ == "__main__":
    asyncio.run(main())