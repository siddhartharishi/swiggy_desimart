import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.models.swiggy import ProductSearchResult
from app.services.swiggy.auth import get_access_token

from app.models.swiggy import AddressResult, ProductSearchResult

SWIGGY_MCP_URL = "https://mcp.swiggy.com/im"


async def search_products(
    address_id: str,
    query: str,
) -> ProductSearchResult:
    """
    Search Swiggy Instamart for products matching a grocery item.
    """

    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=60.0,
    ) as http_client:

        async with streamable_http_client(
            SWIGGY_MCP_URL,
            http_client=http_client,
        ) as (read_stream, write_stream):

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    "search_products",
                    {
                        "addressId": address_id,
                        "query": query,
                    },
                )

                if not result.structured_content:
                    raise RuntimeError(
                        "Swiggy returned no structured search result."
                    )

                return ProductSearchResult.model_validate(
                    result.structured_content
                )

async def get_addresses() -> AddressResult:
    """
    Retrieve the user's saved Swiggy delivery addresses.
    """

    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=60.0,
    ) as http_client:

        async with streamable_http_client(
            SWIGGY_MCP_URL,
            http_client=http_client,
        ) as (read_stream, write_stream):

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    "get_addresses",
                    {},
                )

                if not result.structured_content:
                    raise RuntimeError(
                        "Swiggy returned no structured address result."
                    )

                return AddressResult.model_validate(
                    result.structured_content
                )