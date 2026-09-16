from pydantic import BaseModel, ConfigDict, Field


class ProductPrice(BaseModel):
    mrp: float | None = None

    offer_price: float | None = Field(
        default=None,
        alias="offerPrice",
    )

    unit_level_price: str | None = Field(
        default=None,
        alias="unitLevelPrice",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ProductVariation(BaseModel):
    spin_id: str = Field(alias="spinId")
    sku_id: str = Field(alias="skuId")

    quantity_description: str | None = Field(
        default=None,
        alias="quantityDescription",
    )

    price: ProductPrice | None = None

    is_in_stock_and_available: bool = Field(
        default=True,
        alias="isInStockAndAvailable",
    )

    max_quantity: int | None = Field(
        default=None,
        alias="maxQuantity",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ProductCandidate(BaseModel):
    product_id: str | None = Field(
        default=None,
        alias="productId",
    )

    parent_product_id: str | None = Field(
        default=None,
        alias="parentProductId",
    )

    display_name: str = Field(alias="displayName")

    brand: str | None = None

    in_stock: bool = Field(
        default=True,
        alias="inStock",
    )

    is_available: bool = Field(
        default=True,
        alias="isAvail",
    )

    is_promoted: bool = Field(
        default=False,
        alias="isPromoted",
    )

    variations: list[ProductVariation] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ProductSearchResult(BaseModel):
    next_offset: str | None = Field(
        default=None,
        alias="nextOffset",
    )

    products: list[ProductCandidate] = Field(
        default_factory=list,
    )

    similar_products: list[ProductCandidate] = Field(
        default_factory=list,
        alias="similarProducts",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

class Address(BaseModel):
    id: str
    address_line: str = Field(alias="addressLine")
    phone_number: str | None = Field(
        default=None,
        alias="phoneNumber",
    )
    address_category: str | None = Field(
        default=None,
        alias="addressCategory",
    )
    address_tag: str | None = Field(
        default=None,
        alias="addressTag",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AddressPagination(BaseModel):
    page: int
    page_size: int = Field(alias="pageSize")
    total_pages: int = Field(alias="totalPages")
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AddressResolution(BaseModel):
    needs_user_clarification: bool = Field(
        alias="needsUserClarification",
    )

    candidate_address_ids: list[str] = Field(
        default_factory=list,
        alias="candidateAddressIds",
    )

    default_address_id: str | None = Field(
        default=None,
        alias="defaultAddressId",
    )

    score_used: float | None = Field(
        default=None,
        alias="scoreUsed",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AddressResult(BaseModel):
    addresses: list[Address] = Field(
        default_factory=list,
    )

    pagination: AddressPagination | None = None

    resolution: AddressResolution | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )