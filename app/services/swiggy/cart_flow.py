from app.models.grocery import GroceryItem
from app.services.swiggy.client import update_cart
from app.services.swiggy.ranking import RankedProduct


def show_cart_plan(
    selections: list[tuple[GroceryItem, RankedProduct]],
) -> None:
    """
    Display all products selected by the user before cart mutation.
    """

    print("\n" + "=" * 70)
    print("CART PLAN")
    print("=" * 70)

    if not selections:
        print("\nNo products selected.")
        return

    for index, (grocery_item, selected_product) in enumerate(
        selections,
        start=1,
    ):
        product = selected_product.product
        variation = product.variations[
            selected_product.variation_index
        ]

        print(f"\n{index}. Requested: {grocery_item.original_text}")
        print(f"   Product: {product.display_name}")
        print(f"   Quantity: {variation.quantity_description}")
        print(f"   Match: {selected_product.match}")
        print(f"   Confidence: {selected_product.confidence:.2f}")

        if variation.price:
            price = variation.price.offer_price

            if price is not None:
                print(f"   Price: ₹{price}")


def confirm_cart(
    selections: list[tuple[GroceryItem, RankedProduct]],
) -> bool:
    """
    Ask the user for final approval before modifying the cart.
    """

    if not selections:
        return False

    while True:
        answer = input(
            "\nAdd these products to your Swiggy cart? "
            "(y/n): "
        ).strip().lower()

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please enter y or n.")


async def add_selected_products_to_cart(
    selections: list[tuple[GroceryItem, RankedProduct]],
    address_id: str,
):
    """
    Add all user-approved products to the Swiggy cart.
    """

    results = []

    for grocery_item, selected_product in selections:
        result = await update_cart(
            selected_address_id=address_id,
            spin_id=selected_product.spin_id,
            quantity=int(grocery_item.quantity or 1),
        )

        results.append(
            {
                "grocery_item": grocery_item,
                "selected_product": selected_product,
                "result": result,
            }
        )

    return results