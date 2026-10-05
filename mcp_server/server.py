import json
import os

import httpx
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Wallet MCP Server")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


async def _make_request(
    method: str,
    endpoint: str,
    jwt_token: str,
    json_data: dict | None = None
) -> str:
    headers = {
        "Authorization": f"Bearer {jwt_token.strip()}"
    }
    url = f"{API_BASE_URL.rstrip('/')}{endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=10.0
            )

            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                return json.dumps({
                    "error": True,
                    "status_code": response.status_code,
                    "detail": error_detail
                })

            return json.dumps(response.json())

    except httpx.ConnectError:
        return json.dumps({
            "error": True,
            "status_code": 503,
            "detail": f"Could not connect to FastAPI backend at {API_BASE_URL}. Ensure the server is running."
        })
    except Exception as e:
        return json.dumps({
            "error": True,
            "status_code": 500,
            "detail": str(e)
        })


@mcp.tool()
async def get_balance(jwt_token: str) -> str:
    """Fetch wallet balance for the authenticated user.

    Args:
        jwt_token: JWT bearer access token for authentication.

    Returns:
        JSON string containing wallet balance details or error message.
    """
    return await _make_request(
        method="GET",
        endpoint="/wallet/balance",
        jwt_token=jwt_token
    )


@mcp.tool()
async def credit_wallet(
    jwt_token: str,
    amount: float,
    description: str = ""
) -> str:
    """Credit funds to the authenticated user's wallet.

    Args:
        jwt_token: JWT bearer access token for authentication.
        amount: Positive monetary amount to credit.
        description: Optional description of the credit transaction.

    Returns:
        JSON string containing updated balance and confirmation or error.
    """
    return await _make_request(
        method="POST",
        endpoint="/wallet/credit",
        jwt_token=jwt_token,
        json_data={"amount": amount}
    )


@mcp.tool()
async def debit_wallet(
    jwt_token: str,
    amount: float,
    description: str = ""
) -> str:
    """Debit funds from the authenticated user's wallet.

    Args:
        jwt_token: JWT bearer access token for authentication.
        amount: Positive monetary amount to debit.
        description: Optional description of the debit transaction.

    Returns:
        JSON string containing updated balance and confirmation or error.
    """
    return await _make_request(
        method="POST",
        endpoint="/wallet/debit",
        jwt_token=jwt_token,
        json_data={"amount": amount}
    )


@mcp.tool()
async def get_ledger(jwt_token: str) -> str:
    """Retrieve transaction/ledger history for the authenticated user.

    Args:
        jwt_token: JWT bearer access token for authentication.

    Returns:
        JSON string containing a list of past transactions or error message.
    """
    return await _make_request(
        method="GET",
        endpoint="/wallet/ledger",
        jwt_token=jwt_token
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
