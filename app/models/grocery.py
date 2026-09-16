from pydantic import BaseModel, Field


class GroceryItem(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    original_text: str
    confidence: float = Field(ge=0, le=1)


class GroceryList(BaseModel):
    items: list[GroceryItem]