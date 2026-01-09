"""
PayPal Subscription API
Handles license validation and subscription management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets
import httpx
import os

router = APIRouter(prefix="/api/v1/subscription")

# PayPal API credentials (use environment variables in production)
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "")
PAYPAL_API = os.getenv("PAYPAL_API", "https://api-m.sandbox.paypal.com")  # Use sandbox for testing

# In-memory license store (use database in production)
licenses = {
    "US-PRO-DEMO12345678": {
        "subscription_id": "I-DEMO123456",
        "email": "demo@universalshield.dev",
        "tier": "pro",
        "active": True
    }
}


class SubscriptionActivation(BaseModel):
    subscription_id: str
    email: str


class LicenseValidation(BaseModel):
    license_key: str


@router.post("/activate")
async def activate_subscription(data: SubscriptionActivation):
    """
    Verify PayPal subscription and generate license key.
    Called after user completes PayPal checkout.
    """
    try:
        # 1. Get PayPal access token
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{PAYPAL_API}/v1/oauth2/token",
                auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
                data={"grant_type": "client_credentials"}
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(400, "Failed to authenticate with PayPal")
            
            access_token = auth_response.json()["access_token"]
            
            # 2. Verify subscription status
            sub_response = await client.get(
                f"{PAYPAL_API}/v1/billing/subscriptions/{data.subscription_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if sub_response.status_code != 200:
                raise HTTPException(400, "Invalid subscription ID")
            
            sub_data = sub_response.json()
            
            if sub_data["status"] != "ACTIVE":
                raise HTTPException(400, f"Subscription not active: {sub_data['status']}")
        
        # 3. Generate license key
        license_key = f"US-PRO-{secrets.token_hex(8).upper()}"
        
        # 4. Store license
        licenses[license_key] = {
            "subscription_id": data.subscription_id,
            "email": data.email,
            "tier": "pro",
            "active": True
        }
        
        return {
            "success": True,
            "license_key": license_key,
            "tier": "pro",
            "message": "License activated successfully!"
        }
    
    except httpx.HTTPError as e:
        raise HTTPException(500, f"PayPal API error: {str(e)}")


@router.post("/validate")
async def validate_license(data: LicenseValidation):
    """
    Validate license key from extension.
    Called on extension startup and periodically.
    """
    license_key = data.license_key
    
    if license_key not in licenses:
        return {
            "valid": False,
            "tier": "free",
            "features_enabled": {
                "cloud_ml": False,
                "fraud_ring_detection": False,
                "all_platforms": False,
                "unlimited_scans": False
            }
        }
    
    license_info = licenses[license_key]
    
    # TODO: Periodically check with PayPal if subscription still active
    
    return {
        "valid": license_info["active"],
        "tier": license_info["tier"],
        "features_enabled": {
            "cloud_ml": True,
            "fraud_ring_detection": True,
            "all_platforms": True,
            "unlimited_scans": True
        } if license_info["tier"] == "pro" else {
            "cloud_ml": False,
            "fraud_ring_detection": False,
            "all_platforms": False,
            "unlimited_scans": False
        }
    }


@router.post("/webhook")
async def paypal_webhook(payload: dict):
    """
    Handle PayPal subscription events (cancel, suspend, etc.).
    Configure this URL in PayPal dashboard.
    """
    event_type = payload.get("event_type")
    resource = payload.get("resource", {})
    subscription_id = resource.get("id")
    
    if event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        # Find and deactivate license
        for key, info in licenses.items():
            if info["subscription_id"] == subscription_id:
                licenses[key]["active"] = False
                break
    
    elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
        # Suspend license
        for key, info in licenses.items():
            if info["subscription_id"] == subscription_id:
                licenses[key]["active"] = False
                break
    
    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        # Reactivate license
        for key, info in licenses.items():
            if info["subscription_id"] == subscription_id:
                licenses[key]["active"] = True
                break
    
    return {"status": "ok"}


@router.delete("/cancel/{license_key}")
async def cancel_subscription(license_key: str):
    """
    Cancel subscription and deactivate license.
    User-initiated cancellation.
    """
    if license_key not in licenses:
        raise HTTPException(404, "License not found")
    
    license_info = licenses[license_key]
    subscription_id = license_info["subscription_id"]
    
    try:
        # Cancel subscription with PayPal
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{PAYPAL_API}/v1/oauth2/token",
                auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
                data={"grant_type": "client_credentials"}
            )
            access_token = auth_response.json()["access_token"]
            
            cancel_response = await client.post(
                f"{PAYPAL_API}/v1/billing/subscriptions/{subscription_id}/cancel",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"reason": "User requested cancellation"}
            )
            
            if cancel_response.status_code == 204:
                # Deactivate license
                licenses[license_key]["active"] = False
                return {"success": True, "message": "Subscription cancelled"}
            else:
                raise HTTPException(400, "Failed to cancel subscription")
    
    except httpx.HTTPError as e:
        raise HTTPException(500, f"PayPal API error: {str(e)}")
