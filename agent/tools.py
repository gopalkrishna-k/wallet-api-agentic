import json
import os
import httpx
from langchain_core.tools import tool

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


async def _call_api(
    method: str,
    endpoint: str,
    jwt_token: str,
    json_data: dict | None = None
) -> str:
    headers = {
        "Authorization": f"Bearer {jwt_token.strip()}"
    }

    try:
        if API_BASE_URL == "http://test" or os.getenv("USE_ASGI_TRANSPORT", "false").lower() == "true":
            from app.main import app
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.request(
                    method=method,
                    url=endpoint,
                    headers=headers,
                    json=json_data,
                    timeout=10.0
                )
        else:
            url = f"{API_BASE_URL.rstrip('/')}{endpoint}"
            async with httpx.AsyncClient() as client:
                res = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    timeout=10.0
                )

        if res.status_code >= 400:
            try:
                error_detail = res.json()
            except Exception:
                error_detail = res.text
            return json.dumps({
                "error": True,
                "status_code": res.status_code,
                "detail": error_detail
            })
        return json.dumps(res.json())
    except Exception as e:
        return json.dumps({
            "error": True,
            "status_code": 500,
            "detail": str(e)
        })


@tool
async def get_balance(jwt_token: str) -> str:
    """Fetch the wallet balance for the user corresponding to the JWT token.

    Args:
        jwt_token: The JWT bearer access token of the authenticated user.
    """
    return await _call_api("GET", "/wallet/balance", jwt_token)


@tool
async def credit_wallet(
    jwt_token: str,
    amount: float,
    description: str = ""
) -> str:
    """Credit funds to the user's wallet. FINANCIAL OPERATION requiring human approval.

    Args:
        jwt_token: The JWT bearer access token of the authenticated user.
        amount: Positive float amount to credit.
        description: Description of credit reason.
    """
    return await _call_api(
        "POST",
        "/wallet/credit",
        jwt_token,
        json_data={"amount": amount}
    )


@tool
async def debit_wallet(
    jwt_token: str,
    amount: float,
    description: str = ""
) -> str:
    """Debit funds from the user's wallet. FINANCIAL OPERATION requiring human approval.

    Args:
        jwt_token: The JWT bearer access token of the authenticated user.
        amount: Positive float amount to debit.
        description: Description of debit reason.
    """
    return await _call_api(
        "POST",
        "/wallet/debit",
        jwt_token,
        json_data={"amount": amount}
    )


@tool
async def get_ledger(jwt_token: str) -> str:
    """Retrieve transaction/ledger history for the user corresponding to the JWT token.

    Args:
        jwt_token: The JWT bearer access token of the authenticated user.
    """
    return await _call_api("GET", "/wallet/ledger", jwt_token)


TOOLS = [get_balance, credit_wallet, debit_wallet, get_ledger]

