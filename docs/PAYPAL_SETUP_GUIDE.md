# PayPal Subscription Setup Guide

Complete guide to setting up PayPal subscriptions for UniversalShield PRO tier.

---

## Prerequisites

- PayPal Business account (you already have one for NOMADA)
- Access to PayPal Developer Dashboard
- Domain for webhook URL (api.universalshield.dev)

---

## Step 1: Create Subscription Plans

### 1.1 Login to PayPal Business

1. Go to https://www.paypal.com/businessmanage/
2. Login with your NOMADA PayPal account

### 1.2 Create Product

1. Navigate to **Products & Services** → **Subscriptions**
2. Click **Create Plan**
3. Fill in product details:
   - **Product Name:** UniversalShield Pro
   - **Product Type:** Digital Goods
   - **Product Category:** Software
   - **Product Description:** AI-powered scam detection for LinkedIn, Gmail & Outlook

### 1.3 Create Monthly Plan

1. Click **Add Pricing Plan**
2. Configure plan:
   - **Plan Name:** Pro Monthly
   - **Billing Cycle:** Every 1 month
   - **Price:** $4.99 USD
   - **Setup Fee:** $0
   - **Trial Period:** Optional (7 days free trial recommended)

3. Click **Save**
4. **Copy the Plan ID** (format: `P-XXXXXXXXXXXX`)
   - Save as: `PAYPAL_MONTHLY_PLAN_ID`

### 1.4 Create Annual Plan

1. Click **Add Pricing Plan**
2. Configure plan:
   - **Plan Name:** Pro Annual
   - **Billing Cycle:** Every 12 months
   - **Price:** $39.00 USD (35% discount)
   - **Setup Fee:** $0
   - **Trial Period:** Optional (7 days free trial)

3. Click **Save**
4. **Copy the Plan ID** (format: `P-XXXXXXXXXXXX`)
   - Save as: `PAYPAL_ANNUAL_PLAN_ID`

---

## Step 2: Get API Credentials

### 2.1 Access Developer Dashboard

1. Go to https://developer.paypal.com/dashboard/
2. Login with your PayPal account
3. Navigate to **Apps & Credentials**

### 2.2 Create REST API App

1. Click **Create App**
2. Fill in details:
   - **App Name:** UniversalShield API
   - **App Type:** Merchant
   - **Sandbox/Live:** Start with Sandbox, then create Live

3. Click **Create App**

### 2.3 Get Credentials

**Sandbox (for testing):**
- Client ID: `SANDBOX_CLIENT_ID`
- Secret: `SANDBOX_SECRET`

**Live (for production):**
- Client ID: `LIVE_CLIENT_ID`
- Secret: `LIVE_SECRET`

**Save these securely!**

---

## Step 3: Configure Webhooks

### 3.1 Create Webhook

1. In Developer Dashboard, go to **Webhooks**
2. Click **Add Webhook**
3. Configure:
   - **Webhook URL:** `https://api.universalshield.dev/api/v1/subscription/webhook`
   - **Event types to subscribe to:**
     - ✅ `BILLING.SUBSCRIPTION.ACTIVATED`
     - ✅ `BILLING.SUBSCRIPTION.CANCELLED`
     - ✅ `BILLING.SUBSCRIPTION.SUSPENDED`
     - ✅ `BILLING.SUBSCRIPTION.UPDATED`
     - ✅ `PAYMENT.SALE.COMPLETED`

4. Click **Save**
5. **Copy Webhook ID** for verification

---

## Step 4: Update Environment Variables

Create `.env` file in project root:

```bash
# PayPal Configuration
PAYPAL_MODE=sandbox  # Change to 'live' for production
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_SECRET=your_secret_here
PAYPAL_MONTHLY_PLAN_ID=P-XXXXXXXXXXXX
PAYPAL_ANNUAL_PLAN_ID=P-XXXXXXXXXXXX

# API Configuration
API_URL=https://api.universalshield.dev
DATABASE_URL=postgresql://user:pass@localhost/universalshield

# Security
JWT_SECRET=your_random_secret_here
ENCRYPTION_KEY=your_encryption_key_here
```

---

## Step 5: Test with Sandbox

### 5.1 Create Test Buyer Account

1. In Developer Dashboard, go to **Sandbox** → **Accounts**
2. Click **Create Account**
3. Select **Personal** account type
4. Note the email and password

### 5.2 Test Subscription Flow

1. Start your API server:
   ```bash
   uvicorn src.api.scam_detection_api:app --reload
   ```

2. Create test subscription button:
   ```html
   <div id="paypal-button-container"></div>
   <script src="https://www.paypal.com/sdk/js?client-id=YOUR_SANDBOX_CLIENT_ID&vault=true&intent=subscription"></script>
   <script>
     paypal.Buttons({
       createSubscription: function(data, actions) {
         return actions.subscription.create({
           'plan_id': 'P-XXXXXXXXXXXX' // Your plan ID
         });
       },
       onApprove: function(data, actions) {
         // Call your API to activate license
         fetch('http://localhost:8000/api/v1/subscription/activate', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
             subscription_id: data.subscriptionID,
             email: 'user@example.com'
           })
         }).then(res => res.json())
           .then(data => {
             alert('License Key: ' + data.license_key);
           });
       }
     }).render('#paypal-button-container');
   </script>
   ```

3. Test the flow:
   - Click PayPal button
   - Login with sandbox buyer account
   - Complete subscription
   - Verify license key is generated

---

## Step 6: Go Live

### 6.1 Switch to Live Credentials

1. Update `.env`:
   ```bash
   PAYPAL_MODE=live
   PAYPAL_CLIENT_ID=your_live_client_id
   PAYPAL_SECRET=your_live_secret
   ```

2. Update webhook URL to production domain

### 6.2 Update Payment Page

Create `payment.html` for your website:

```html
<!DOCTYPE html>
<html>
<head>
  <title>UniversalShield Pro - Subscribe</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
    .plan { border: 2px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
    .plan.featured { border-color: #dc2626; }
    .price { font-size: 48px; font-weight: bold; color: #dc2626; }
    .features { list-style: none; padding: 0; }
    .features li { padding: 8px 0; }
    .features li:before { content: "✅ "; }
  </style>
</head>
<body>
  <h1>🛡️ UniversalShield Pro</h1>
  <p>Upgrade to Pro for unlimited scans and advanced AI protection</p>

  <div class="plan">
    <h2>Monthly Plan</h2>
    <div class="price">$4.99<span style="font-size:20px">/month</span></div>
    <ul class="features">
      <li>Unlimited scans</li>
      <li>Cloud ML analysis</li>
      <li>All platforms (LinkedIn, Gmail, Outlook)</li>
      <li>Fraud ring detection</li>
      <li>Priority support</li>
    </ul>
    <div id="paypal-button-monthly"></div>
  </div>

  <div class="plan featured">
    <h2>Annual Plan <span style="color:#10b981">SAVE 35%</span></h2>
    <div class="price">$39<span style="font-size:20px">/year</span></div>
    <p style="color:#6b7280">Just $3.25/month - Save $20.88/year!</p>
    <ul class="features">
      <li>All Monthly features</li>
      <li>35% discount</li>
      <li>Best value</li>
    </ul>
    <div id="paypal-button-annual"></div>
  </div>

  <script src="https://www.paypal.com/sdk/js?client-id=YOUR_LIVE_CLIENT_ID&vault=true&intent=subscription"></script>
  <script>
    // Monthly button
    paypal.Buttons({
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': 'YOUR_MONTHLY_PLAN_ID'
        });
      },
      onApprove: function(data, actions) {
        const email = prompt('Enter your email for license delivery:');
        fetch('https://api.universalshield.dev/api/v1/subscription/activate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            subscription_id: data.subscriptionID,
            email: email
          })
        }).then(res => res.json())
          .then(result => {
            alert('✅ Success! Your license key: ' + result.license_key + '\n\nSave this key and enter it in the extension settings.');
            window.location.href = '/success.html?key=' + result.license_key;
          });
      }
    }).render('#paypal-button-monthly');

    // Annual button
    paypal.Buttons({
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': 'YOUR_ANNUAL_PLAN_ID'
        });
      },
      onApprove: function(data, actions) {
        const email = prompt('Enter your email for license delivery:');
        fetch('https://api.universalshield.dev/api/v1/subscription/activate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            subscription_id: data.subscriptionID,
            email: email
          })
        }).then(res => res.json())
          .then(result => {
            alert('✅ Success! Your license key: ' + result.license_key + '\n\nSave this key and enter it in the extension settings.');
            window.location.href = '/success.html?key=' + result.license_key;
          });
      }
    }).render('#paypal-button-annual');
  </script>
</body>
</html>
```

---

## Step 7: Revenue Tracking

### Expected Revenue (5% conversion rate):

| Users | Pro Users | Monthly Revenue | Annual Revenue |
|-------|-----------|-----------------|----------------|
| 1,000 | 50 | $250 | $3,000 |
| 10,000 | 500 | $2,500 | $30,000 |
| 100,000 | 5,000 | $25,000 | $300,000 |

### PayPal Fees:
- Transaction fee: 3.49% + $0.49
- Monthly $4.99: You keep ~$4.65
- Annual $39: You keep ~$37.14

---

## Troubleshooting

### Webhook not receiving events:
1. Check webhook URL is publicly accessible
2. Verify SSL certificate is valid
3. Check PayPal dashboard for webhook delivery logs

### Subscription not activating:
1. Verify Plan ID is correct
2. Check API credentials are for correct environment (sandbox vs live)
3. Review server logs for errors

### License validation failing:
1. Ensure license key is stored correctly
2. Check database connection
3. Verify subscription is still active in PayPal

---

## Security Best Practices

1. **Never commit credentials to git**
   - Use `.env` file (add to `.gitignore`)
   - Use environment variables in production

2. **Verify webhook signatures**
   - Implement PayPal webhook signature verification
   - Reject unsigned requests

3. **Use HTTPS only**
   - All API endpoints must use SSL
   - Redirect HTTP to HTTPS

4. **Rate limit API endpoints**
   - Prevent abuse
   - Already implemented in scam_detection_api.py

---

## Support

- PayPal Developer Docs: https://developer.paypal.com/docs/subscriptions/
- PayPal Support: https://www.paypal.com/businesshelp/
- UniversalShield Issues: https://github.com/jcuberogit/universalshield/issues

---

**Next:** Once PayPal is configured, proceed to Phase 7 (Chrome Web Store submission)
