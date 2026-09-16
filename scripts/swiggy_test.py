import asyncio

from app.services.swiggy.client import get_addresses, search_products
from app.services.swiggy.matching import rank_product_variations
from app.models.grocery import GroceryItem

async def main():
    # 1. Get the user's saved addresses
    print("Fetching Swiggy addresses...\n")

    address_result = await get_addresses()

    print("Available addresses:\n")

    for index, address in enumerate(
        address_result.addresses,
        start=1,
    ):
        print(
            f"{index}. "
            f"{address.address_tag or 'Address'}"
        )
        print(f"   {address.address_line}")
        print()

    # 2. Choose an address
    choice = int(
        input("Choose an address number: ")
    )

    selected_address = address_result.addresses[
        choice - 1
    ]

    print(
        f"\nUsing address: "
        f"{selected_address.address_tag or 'Address'}"
    )

    # 3. Search for a grocery item
    query = input(
        "\nWhat grocery item should we search for? "
    ).strip()

    print(f"\nSearching Swiggy for '{query}'...\n")

    result = await search_products(
        address_id=selected_address.id,
        query=query,
    )

    #matching 
    grocery_item = GroceryItem(
        name=query,
        quantity=1,
        unit="kg",
        original_text=query,
        confidence=1.0,
    )

    ranked = rank_product_variations(
        grocery_item=grocery_item,
        products=result.products,
    )

    print("\nRanked candidates:\n")

    for index, candidate in enumerate(
        ranked[:10],
        start=1,
    ):
        print(
            f"{index}. "
            f"{candidate.product.display_name} | "
            f"{candidate.variation.quantity_description} | "
            f"₹{candidate.variation.price.offer_price if candidate.variation.price else None} | "
            f"score={candidate.score:.2f}"
        )

    # 4. Display direct matches
    print(
        f"Direct matches: "
        f"{len(result.products)}"
    )

    for product in result.products:
        print(f"\n{product.display_name}")

        if product.brand:
            print(f"Brand: {product.brand}")

        for variation in product.variations:
            price = variation.price

            offer_price = (
                price.offer_price
                if price
                else None
            )

            print(
                f"  - {variation.quantity_description}"
                f" | ₹{offer_price}"
            )

    # 5. Display similar matches
    print(
        f"\nSimilar matches: "
        f"{len(result.similar_products)}"
    )


if __name__ == "__main__":
    asyncio.run(main())