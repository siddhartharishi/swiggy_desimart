from fastapi import FastAPI

from app.api.grocery import router as grocery_router


app = FastAPI(
    title="Grocery Agent",
    description="AI-powered handwritten grocery list extraction API.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
    }


app.include_router(grocery_router)