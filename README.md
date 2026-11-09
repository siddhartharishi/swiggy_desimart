# 🛒 AI Grocery Shopping Agent

**Turn handwritten grocery lists into a ready-to-shop Instamart cart using AI and MCP.**

An AI-powered grocery shopping assistant that converts handwritten grocery lists into structured data, finds relevant products on Swiggy Instamart, recommends the best matches, and lets users add their selections to their cart.

Instead of manually searching for every grocery item, users simply upload a picture of their handwritten list. The system reads it, understands the requested items and quantities, finds matching products, and helps build a shopping cart.

## ✨ Features

- **Handwritten Grocery Recognition:** Upload a handwritten grocery list and extract items using a multimodal AI model.
- **Structured Data Extraction:** Convert handwritten text into structured JSON containing product names, quantities, units, and confidence scores.
- **AI-Powered Product Matching:** Use an LLM to evaluate Instamart search results and identify relevant product matches.
- **Smart Recommendations:** Rank products by match quality and confidence, with exact matches and reasonable alternatives.
- **Product Selection:** Review recommendations and choose the preferred product variation.
- **Swiggy Instamart Integration:** Search products, retrieve saved delivery addresses, and manage the cart using Swiggy MCP.
- **Human-in-the-Loop:** Keep the user in control of product selection and cart updates.
- **Cart Verification:** Retrieve the cart after updates to inspect the resulting cart contents.

## 🚀 How It Works

```text
         Handwritten Grocery List
                   │
                   ▼
            Upload Image
                   │
                   ▼
          Multimodal AI (LLM)
             OpenRouter
                   │
                   ▼
         Structured Extraction
          Name, Quantity, Unit
                   │
                   ▼
          Select Delivery Address
                   │
                   ▼
          Swiggy Instamart MCP
             Product Search
                   │
                   ▼
          AI Product Matching
         Exact / Acceptable / Poor
                   │
                   ▼
           Ranked Recommendations
                   │
                   ▼
            User Selects Products
                   │
                   ▼
              Cart Approval
                   │
                   ▼
             Update Instamart Cart
                   │
                   ▼
                Get Cart
```

## 🧠 AI Architecture

### 1. Handwritten List Extraction

The application uses a multimodal model through OpenRouter to read handwritten grocery lists.

The model extracts grocery items into a structured format.

Example input:

```text
Potato 1kg
Onion 2kg
Milk 2 packets
Rice 5kg
```

Example output:

```json
{
  "items": [
    {
      "name": "potato",
      "quantity": 1,
      "unit": "kg",
      "original_text": "Potato 1kg",
      "confidence": 0.97
    },
    {
      "name": "onion",
      "quantity": 2,
      "unit": "kg",
      "original_text": "Onion 2kg",
      "confidence": 0.95
    },
    {
      "name": "milk",
      "quantity": 2,
      "unit": "packets",
      "original_text": "Milk 2 packets",
      "confidence": 0.96
    }
  ]
}
```

The extracted data is validated using Pydantic models.

### 2. AI-Powered Product Matching

For every extracted grocery item, the application searches Swiggy Instamart for relevant products.

An LLM evaluates the returned product candidates based on:

- Product name and relevance
- Brand and product type
- Quantity and variation
- Product availability
- Whether the candidate is a reasonable alternative

Each recommendation receives:

| Field | Description |
|---|---|
| Match | Exact, acceptable, or poor |
| Confidence | Model confidence score |
| Reason | Explanation for the recommendation |
| Variation | Selected product variation |
| Price | Product pricing information |

The matching system prioritizes useful recommendations rather than enforcing unnecessarily strict quantity equivalence.

### 3. Swiggy MCP Integration

The application communicates with Swiggy Instamart through the Model Context Protocol (MCP).

It uses OAuth 2.1 with PKCE for authentication and the Streamable HTTP transport for MCP communication.

The integration supports operations including:

- Retrieving saved delivery addresses
- Searching Instamart products
- Updating the shopping cart
- Retrieving the current cart

The user reviews and approves product selections before cart operations are performed.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI |
| AI / Multimodal | OpenRouter, Vision-Language Models |
| AI Product Matching | LLM-based structured evaluation |
| AI Integration | HTTPX |
| Commerce Integration | Swiggy Instamart MCP |
| MCP SDK | Python MCP SDK |
| Authentication | OAuth 2.1, PKCE |
| Data Validation | Pydantic |
| Async HTTP | HTTPX, aiohttp |
| Testing | Pytest |

## 📁 Project Structure

```text
swiggy_desimart/
│
├── app/
│   ├── api/
│   │   └── grocery.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── models/
│   │   ├── grocery.py
│   │   └── swiggy.py
│   │
│   ├── prompts/
│   │   └── grocery_extraction.py
│   │
│   ├── services/
│   │   ├── vision.py
│   │   │
│   │   └── swiggy/
│   │       ├── auth.py
│   │       ├── client.py
│   │       ├── address.py
│   │       ├── matching.py
│   │       ├── llm_matching.py
│   │       ├── ranking.py
│   │       ├── grocery_flow.py
│   │       ├── selection.py
│   │       ├── list_flow.py
│   │       └── cart_flow.py
│   │
│   └── main.py
│
├── scripts/
│   ├── swiggy_test.py
│   ├── multi_item_test.py
│   └── image_flow_test.py
│
├── tests/
│   └── test_grocery.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- A
