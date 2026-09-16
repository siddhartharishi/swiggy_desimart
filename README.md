# Grocery Agent

Grocery Agent is a small backend for converting a photographed handwritten Indian household grocery list into validated, structured JSON. It is designed for English, Hindi, Telugu, and mixed-language lists.

## Phase 1 scope

This phase accepts an image, sends it to a hosted multimodal Qwen-compatible model, normalizes and translates grocery entries, and returns the result. Uploaded images are read in memory only and are never persisted.

Swiggy MCP, shopping workflows, databases, authentication, and frontend work are intentionally out of scope until Phase 2.

## Architecture

`POST /api/v1/grocery/parse` validates and reads the multipart image, then depends on the provider-neutral `VisionService` interface. `QwenVisionService` is the initial implementation and uses an OpenAI-compatible chat-completions endpoint. Its structured response is validated by Pydantic before being returned to the caller. A different provider can be added by implementing `VisionService` and changing the dependency wiring, without changing the route.

## Project structure

```
grocery-agent/
├── app/
│   ├── api/grocery.py          # HTTP endpoint and upload validation
│   ├── core/config.py          # environment configuration
│   ├── models/grocery.py       # Pydantic response models
│   ├── prompts/grocery_extraction.py
│   ├── services/vision/base.py # provider contract
│   ├── services/vision/qwen.py # Qwen-compatible provider
│   └── main.py
├── tests/test_grocery.py
├── .env.example
├── requirements.txt
└── run.sh
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set the endpoint and credentials for a hosted deployment that supports Qwen3-VL-8B-Instruct (or its provider-equivalent model):

```dotenv
QWEN_API_KEY=your-provider-key
QWEN_BASE_URL=https://your-provider.example/v1
QWEN_MODEL=qwen3-vl-8b-instruct
```

`QWEN_BASE_URL` is the base path before `/chat/completions`. The service fails the parse request with a clear configuration error if the API key or base URL is absent. Never commit `.env`.

The default upload limit is 10 MiB. Set `MAX_IMAGE_SIZE_BYTES` to change it. `VISION_REQUEST_TIMEOUT_SECONDS` controls provider request timeout. The service logs request metadata and item counts, not raw image bytes or credentials.

## Run

```bash
uvicorn app.main:app --reload
```

or:

```bash
./run.sh
```

FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/grocery/parse \
  -F "image=@/path/to/grocery-list.png;type=image/png"
```

Example response:

```json
{
  "items": [
    {
      "name": "rice",
      "quantity": 5,
      "unit": "kg",
      "original_text": "బియ్యం 5kg",
      "detected_language": "Telugu",
      "confidence": 0.96
    }
  ]
}
```

If a list entry has no written quantity, `quantity` is `null`; this avoids making up a number. An absent unit is an empty string.

## Tests

```bash
pytest
```

Tests use a mock `VisionService` and `httpx.MockTransport`; they make no external API calls.

## Current limitations

Extraction quality depends on handwriting clarity and the selected model/provider. The provider adapter assumes an OpenAI-compatible `/chat/completions` API with JSON-schema response-format support. Provider-specific payload differences belong only in `app/services/vision/qwen.py`.

## Future direction

Phase 2 can take the validated `GroceryList` and integrate it with Swiggy Instamart through Swiggy MCP. No Swiggy code is included in this phase.
