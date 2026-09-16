
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.grocery import GroceryList
from app.services.vision import extract_grocery_list


router = APIRouter(
    prefix="/api/v1/grocery",
    tags=["grocery"],
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


@router.post("/parse", response_model=GroceryList)
async def parse_grocery_image(
    image: UploadFile = File(...),
) -> GroceryList:
    """
    Extract grocery items from a handwritten grocery-list image.
    """

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image type. "
                "Use JPEG, PNG, WEBP, or GIF."
            ),
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    try:
        return await extract_grocery_list(
            image_bytes=image_bytes,
            content_type=image.content_type,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Vision model request failed: {str(exc)}",
        ) from exc