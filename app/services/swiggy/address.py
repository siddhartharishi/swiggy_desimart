from app.models.swiggy import Address
from app.services.swiggy.client import get_addresses


async def select_address() -> Address:
    """
    Fetch saved Swiggy addresses and let the user select one.
    """

    result = await get_addresses()

    if not result.addresses:
        raise RuntimeError(
            "No saved Swiggy addresses were found."
        )

    print("\nSAVED ADDRESSES")
    print("=" * 70)

    for index, address in enumerate(result.addresses, start=1):
        print(f"\n{index}. {address.address_line}")

        if address.address_tag:
            print(f"   Tag: {address.address_tag}")

        if address.address_category:
            print(f"   Category: {address.address_category}")

    while True:
        choice = input(
            "\nSelect a delivery address "
            f"(1-{len(result.addresses)}): "
        ).strip()

        try:
            index = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= index <= len(result.addresses):
            selected_address = result.addresses[index - 1]

            print(
                f"\nSelected address: "
                f"{selected_address.address_line}"
            )

            return selected_address

        print(
            f"Please enter a number between "
            f"1 and {len(result.addresses)}."
        )