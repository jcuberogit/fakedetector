"""
Payment API - Stripe Integration for UniversalShield Pro Subscriptions
Handles subscription creation, webhook events, and license generation
"""

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional, Dict
import os
import secrets
import hmac
import hashlib

# Stripe will be imported when available
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("⚠️  Stripe not installed. Run: pip install stripe")

from src.db.database import DatabaseService

router = APIRouter(prefix="/api/v1/payment")

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')
STRIPE_PRICE_ID_MONTHLY = os.getenv('STRIPE_PRICE_ID_MONTHLY', 'price_...')
STRIPE_PRICE_ID_ANNUAL = os.getenv('STRIPE_PRICE_ID_ANNUAL', 'price_...')

if STRIPE_AVAILABLE:
    stripe.api_key = STRIPE_SECRET_KEY

# Initialize database
db = DatabaseService()


class CreateCheckoutRequest(BaseModel):
    plan: str  # 'monthly' or 'annual'
    email: str
    success_url: str
    cancel_url: str


class ActivateSubscriptionRequest(BaseModel):
    session_id: str


@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    Create Stripe Checkout session for subscription.
    Returns checkout URL for user to complete payment.
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing unavailable. Please contact support."
        )
    
    try:
        # Determine price ID based on plan
        price_id = STRIPE_PRICE_ID_MONTHLY if request.plan == 'monthly' else STRIPE_PRICE_ID_ANNUAL
        
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.cancel_url,
            metadata={
                'product': 'universalshield_pro',
                'plan': request.plan
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout creation failed: {str(e)}")


@router.post("/activate-subscription")
async def activate_subscription(request: ActivateSubscriptionRequest):
    """
    Activate subscription after successful Stripe payment.
    Generates license key and stores in database.
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing unavailable. Please contact support."
        )
    
    try:
        # Retrieve checkout session
        session = stripe.checkout.Session.retrieve(request.session_id)
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get subscription ID
        subscription_id = session.subscription
        customer_email = session.customer_email or session.customer_details.email
        
        # Check if license already exists for this subscription
        # (prevent duplicate activation)
        existing = db.conn.cursor()
        existing.execute(
            "SELECT license_key FROM licenses WHERE subscription_id = %s",
            (subscription_id,)
        )
        result = existing.fetchone()
        existing.close()
        
        if result:
            return {
                "success": True,
                "license_key": result[0],
                "message": "Subscription already activated"
            }
        
        # Generate new license key
        license_key = db.create_license(
            email=customer_email,
            tier='pro',
            subscription_id=subscription_id
        )
        
        if not license_key:
            raise HTTPException(status_code=500, detail="License generation failed")
        
        return {
            "success": True,
            "license_key": license_key,
            "tier": "pro",
            "email": customer_email,
            "message": "Subscription activated successfully!"
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events (subscription updates, cancellations).
    This endpoint is called by Stripe when subscription events occur.
    """
    if not STRIPE_AVAILABLE:
        return {"status": "ok"}
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    event_type = event['type']
    data = event['data']['object']
    
    if event_type == 'customer.subscription.deleted':
        # Subscription cancelled - deactivate license
        subscription_id = data['id']
        
        # Find and deactivate license
        cursor = db.conn.cursor()
        cursor.execute(
            "UPDATE licenses SET active = FALSE WHERE subscription_id = %s",
            (subscription_id,)
        )
        db.conn.commit()
        cursor.close()
        
        print(f"🔴 Subscription cancelled: {subscription_id}")
    
    elif event_type == 'customer.subscription.updated':
        # Subscription updated (e.g., plan change)
        subscription_id = data['id']
        status = data['status']
        
        # Update license status based on subscription status
        active = status in ['active', 'trialing']
        
        cursor = db.conn.cursor()
        cursor.execute(
            "UPDATE licenses SET active = %s WHERE subscription_id = %s",
            (active, subscription_id)
        )
        db.conn.commit()
        cursor.close()
        
        print(f"🔄 Subscription updated: {subscription_id} - Status: {status}")
    
    elif event_type == 'invoice.payment_failed':
        # Payment failed - suspend license temporarily
        subscription_id = data['subscription']
        
        cursor = db.conn.cursor()
        cursor.execute(
            "UPDATE licenses SET active = FALSE WHERE subscription_id = %s",
            (subscription_id,)
        )
        db.conn.commit()
        cursor.close()
        
        print(f"⚠️  Payment failed for subscription: {subscription_id}")
    
    return {"status": "ok"}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    return {
        "plans": [
            {
                "id": "monthly",
                "name": "Pro Monthly",
                "price": 4.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "Unlimited scans",
                    "Cloud ML analysis",
                    "Gmail & Outlook support",
                    "Fraud ring detection",
                    "Priority support"
                ]
            },
            {
                "id": "annual",
                "name": "Pro Annual",
                "price": 39.00,
                "currency": "USD",
                "interval": "year",
                "savings": "34% off",
                "features": [
                    "Unlimited scans",
                    "Cloud ML analysis",
                    "Gmail & Outlook support",
                    "Fraud ring detection",
                    "Priority support",
                    "2 months free"
                ]
            }
        ]
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    license_key: str,
    x_license_key: Optional[str] = Header(None)
):
    """
    Cancel a subscription.
    User must provide their license key.
    """
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment processing unavailable. Please contact support."
        )
    
    # Validate license key
    if license_key != x_license_key:
        raise HTTPException(status_code=403, detail="Invalid license key")
    
    # Get subscription ID from database
    license_info = db.validate_license(license_key)
    
    if not license_info:
        raise HTTPException(status_code=404, detail="License not found")
    
    cursor = db.conn.cursor()
    cursor.execute(
        "SELECT subscription_id FROM licenses WHERE license_key = %s",
        (license_key,)
    )
    result = cursor.fetchone()
    cursor.close()
    
    if not result or not result[0]:
        raise HTTPException(status_code=400, detail="No active subscription found")
    
    subscription_id = result[0]
    
    try:
        # Cancel Stripe subscription
        stripe.Subscription.delete(subscription_id)
        
        # Deactivate license
        db.deactivate_license(license_key)
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully"
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Cancellation failed: {str(e)}")
