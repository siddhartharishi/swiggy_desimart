from app.services.swiggy.ranking import RankedProduct


def select_product(
    ranked_products: list[RankedProduct],
) -> RankedProduct | None:
    """
    Display suitable product matches and let the user select one.
    """

    selectable = [
        product
        for product in ranked_products
        if product.match in {"exact", "acceptable"}
    ]

    if not selectable:
        print("\nNo suitable products found.")
        return None

    print("\nSELECT A PRODUCT")
    print("=" * 70)

    for index, candidate in enumerate(selectable, start=1):
        product = candidate.product
        variation = product.variations[candidate.variation_index]

        print(f"\n{index}. {product.display_name}")
        print(f"   Match: {candidate.match}")
        print(f"   Confidence: {candidate.confidence:.2f}")
        print(f"   Quantity: {variation.quantity_description}")

        if variation.price:
            price = variation.price.offer_price
            if price is not None:
                print(f"   Price: ₹{price}")

        print(f"   Reason: {candidate.reason}")

    while True:
        choice = input(
            f"\nSelect a product (1-{len(selectable)}) "
            "or 0 to skip: "
        ).strip()

        try:
            index = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if index == 0:
            return None

        if 1 <= index <= len(selectable):
            selected = selectable[index - 1]

            print(
                f"\nSelected: "
                f"{selected.product.display_name}"
            )

            return selected

        print(
            f"Please enter a number between "
            f"1 and {len(selectable)}, or 0 to skip."
        )