# ============================================================
#  mpesa.py  –  M-Pesa Daraja API integration
#  Supports both SANDBOX and PRODUCTION modes (set in config.py)
# ============================================================

import base64
import logging
import re
from datetime import datetime
from typing import Optional

import httpx
import config

logger = logging.getLogger(__name__)

SANDBOX_BASE  = "https://sandbox.safaricom.co.ke"
PROD_BASE     = "https://api.safaricom.co.ke"

def _base_url() -> str:
    return SANDBOX_BASE if config.MPESA_SANDBOX else PROD_BASE


async def get_access_token() -> Optional[str]:
    """Fetch an OAuth2 bearer token from Daraja."""
    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    creds = base64.b64encode(
        f"{config.MPESA_CONSUMER_KEY}:{config.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers={"Authorization": f"Basic {creds}"})
            resp.raise_for_status()
            return resp.json().get("access_token")
    except Exception as exc:
        logger.error(f"M-Pesa token fetch failed: {exc}")
        return None


def _build_password() -> tuple[str, str]:
    """Return (password_b64, timestamp) for STK push."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{config.MPESA_SHORTCODE}{config.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def normalise_phone(phone: str) -> str:
    """Convert 07XXXXXXXX / 01XXXXXXXX → 2547XXXXXXXX."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if phone.startswith("+"):
        phone = phone[1:]
    return phone


def validate_kenyan_phone(phone: str) -> bool:
    """Return True if phone looks like a valid Kenyan mobile number."""
    normalised = normalise_phone(phone)
    return bool(re.match(r"^254[71]\d{8}$", normalised))


async def stk_push(phone: str, amount: int, account_ref: str,
                   description: str = "Premium Channel Subscription") -> dict:
    """
    Trigger an M-Pesa STK push to `phone` for `amount` KSH.
    Returns the full Daraja JSON response or {"error": ...} on failure.
    """
    token = await get_access_token()
    if not token:
        return {"error": "Could not authenticate with M-Pesa. Try again shortly."}

    password, timestamp = _build_password()
    payload = {
        "BusinessShortCode": config.MPESA_SHORTCODE,
        "Password":          password,
        "Timestamp":         timestamp,
        "TransactionType":   "CustomerPayBillOnline",
        "Amount":            amount,
        "PartyA":            normalise_phone(phone),
        "PartyB":            config.MPESA_SHORTCODE,
        "PhoneNumber":       normalise_phone(phone),
        "CallBackURL":       config.MPESA_CALLBACK_URL,
        "AccountReference":  account_ref[:12],   # Daraja limit
        "TransactionDesc":   description[:13],
    }
    url = f"{_base_url()}/mpesa/stkpush/v1/processrequest"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type":  "application/json"},
            )
            data = resp.json()
            logger.info(f"STK Push response: {data}")
            return data
    except Exception as exc:
        logger.error(f"STK Push failed: {exc}")
        return {"error": str(exc)}


async def query_stk_status(checkout_request_id: str) -> dict:
    """Query the status of a pending STK push."""
    token = await get_access_token()
    if not token:
        return {"error": "Auth failed"}

    password, timestamp = _build_password()
    payload = {
        "BusinessShortCode":  config.MPESA_SHORTCODE,
        "Password":           password,
        "Timestamp":          timestamp,
        "CheckoutRequestID":  checkout_request_id,
    }
    url = f"{_base_url()}/mpesa/stkpushquery/v1/query"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type":  "application/json"},
            )
            return resp.json()
    except Exception as exc:
        return {"error": str(exc)}
