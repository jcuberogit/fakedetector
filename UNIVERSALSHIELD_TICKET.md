# UniversalShield Implementation Ticket

## Project Overview
**Repo:** https://github.com/jcuberogit/universalshield  
**Status:** Extension working locally, needs API integration  
**Priority:** High  
**Estimated Time:** 2-3 days  

---

## Current State

### Completed ✅
- [x] Chrome extension structure (Manifest V3)
- [x] Local scam pattern detection (100+ patterns EN/ES)
- [x] Risk scoring engine (detector.js)
- [x] Visual badges for suspicious messages
- [x] Popup with stats dashboard
- [x] GitHub repo created and pushed
- [x] paradigm.fraud.agent included in repo

### Not Working ❌
- [ ] Extension not connected to fraud agent API
- [ ] No VPS deployment
- [ ] No cloud ML analysis
- [ ] No GNN fraud ring detection
- [ ] No user authentication
- [ ] Not on Chrome Web Store

---

## Implementation Tasks

### Phase 1: API Endpoint (Day 1 Morning)

#### Task 1.1: Create REST API for Fraud Agent
**File:** `src/api/scam_detection_api.py`

```python
# Endpoints needed:
POST /api/v1/analyze-message
  - Input: { message_text, sender_info, platform }
  - Output: { risk_score, risk_level, patterns_matched, recommendations }

POST /api/v1/report-scam
  - Input: { message_text, platform, user_report }
  - Output: { success, report_id }

GET /api/v1/patterns/latest
  - Output: { patterns, version, updated_at }
```

#### Task 1.2: Add CORS Support
- Allow requests from Chrome extension
- Secure with API key or JWT

#### Task 1.3: Rate Limiting
- Free tier: 50 requests/day
- Pro tier: Unlimited

---

### Phase 2: VPS Deployment (Day 1 Afternoon)

#### Task 2.1: Choose VPS Provider
**Options:**
| Provider | Spec | Cost |
|----------|------|------|
| DigitalOcean | 2 vCPU, 4GB | $24/mo |
| Hetzner | 2 vCPU, 4GB | $10/mo |
| Vultr | 2 vCPU, 4GB | $20/mo |

**Recommended:** Hetzner (best price/performance)

#### Task 2.2: Deploy Fraud Agent
```bash
# On VPS:
git clone https://github.com/jcuberogit/universalshield.git
cd universalshield
pip install -r requirements.txt
# Configure environment variables
# Start API server with gunicorn/uvicorn
```

#### Task 2.3: Setup Domain & SSL
- Domain: api.universalshield.dev or shield.paradigm.dev
- SSL: Let's Encrypt (free)

#### Task 2.4: Setup Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name api.universalshield.dev;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

### Phase 3: Connect Extension to API (Day 2 Morning)

#### Task 3.1: Update Extension Config
**File:** `extensions/UniversalShield/src/config.js`
```javascript
const CONFIG = {
  API_URL: 'https://api.universalshield.dev',
  API_VERSION: 'v1',
  FREE_DAILY_LIMIT: 50,
  ENABLE_CLOUD_ML: true
};
```

#### Task 3.2: Update Content Script
**File:** `extensions/UniversalShield/src/content.js`
- Add API call for suspicious messages
- Fallback to local detection if API unavailable
- Cache API responses

#### Task 3.3: Update Background Script
**File:** `extensions/UniversalShield/src/background.js`
- Handle API authentication
- Manage daily request quota
- Sync patterns from API

---

### Phase 4: ML Integration (Day 2 Afternoon)

#### Task 4.1: Create ML Endpoint
Connect to existing fraud agent services:
- `ml_service.py` - XGBoost model
- `gnn_service.py` - Fraud ring detection
- `rules_engine_service.py` - Dynamic rules

#### Task 4.2: Train Scam Detection Model
**Input features:**
- Message length
- Keyword density
- Urgency score
- Link analysis
- Sender profile age
- Connection count

**Output:**
- Scam probability (0-100)
- Scam category
- Confidence score

---

### Phase 5: Freemium Implementation (Day 3)

#### Task 5.1: User Tiers
```javascript
const TIERS = {
  FREE: {
    dailyScans: 50,
    cloudML: false,
    platforms: ['linkedin'],
    fraudRingDetection: false
  },
  PRO: {
    dailyScans: Infinity,
    cloudML: true,
    platforms: ['linkedin', 'gmail', 'outlook'],
    fraudRingDetection: true,
    price: 4.99 // monthly
  }
};
```

#### Task 5.2: Payment Integration
**Options:**
- Stripe (recommended)
- Gumroad (simpler)
- Ko-fi (donations)

#### Task 5.3: License Key System
- Generate license keys for Pro users
- Validate in extension
- Store in chrome.storage.sync

---

### Phase 6: Chrome Web Store (Day 3)

#### Task 6.1: Prepare Assets
- [ ] 128x128 icon (PNG)
- [ ] 440x280 small promo tile
- [ ] 1280x800 large promo tile
- [ ] 5 screenshots (1280x800)
- [ ] Privacy policy URL
- [ ] Detailed description

#### Task 6.2: Developer Account
- Create Google Developer account
- Pay $5 one-time fee
- Verify identity

#### Task 6.3: Submit for Review
- Prepare justification for permissions
- Expect 1-3 days review time

---

## Monetization Strategy

### Pricing
| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 50 scans/day, local detection, LinkedIn only |
| **Pro** | $4.99/mo | Unlimited, cloud ML, all platforms, GNN |
| **Annual** | $39/yr | Pro features, 35% discount |

### Revenue Projections
| Users | Free | Pro (5%) | Monthly Revenue |
|-------|------|----------|-----------------|
| 1,000 | 950 | 50 | $250 |
| 10,000 | 9,500 | 500 | $2,500 |
| 100,000 | 95,000 | 5,000 | $25,000 |

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Extension                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Content  │  │ Detector │  │  Popup   │  │Background│    │
│  │  Script  │──│  Engine  │  │   UI     │  │  Worker  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       │              │                            │          │
│       └──────────────┼────────────────────────────┘          │
│                      │ Local detection (Free)                │
│                      ▼                                       │
│              ┌──────────────┐                               │
│              │  API Client  │                               │
│              └──────────────┘                               │
└─────────────────────│───────────────────────────────────────┘
                      │ Cloud ML (Pro)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    VPS (Hetzner)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Nginx + SSL                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            FastAPI / Uvicorn (Port 8000)              │   │
│  └──────────────────────────────────────────────────────┘   │
│       │              │              │              │         │
│  ┌────────┐    ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Auth  │    │ ML Model │  │   GNN    │  │  Rules   │    │
│  │Service │    │ (XGBoost)│  │ Service  │  │ Engine   │    │
│  └────────┘    └──────────┘  └──────────┘  └──────────┘    │
│                      │              │              │         │
│                      └──────────────┴──────────────┘         │
│                                 │                            │
│                        ┌──────────────┐                     │
│                        │   Database   │                     │
│                        │  (SQLite/PG) │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `src/api/scam_detection_api.py` | FastAPI REST endpoints |
| `src/api/auth_middleware.py` | API key / JWT validation |
| `src/api/rate_limiter.py` | Request rate limiting |
| `extensions/UniversalShield/src/config.js` | Extension configuration |
| `extensions/UniversalShield/src/apiClient.js` | API communication |
| `deploy/docker-compose.yml` | Container deployment |
| `deploy/nginx.conf` | Reverse proxy config |
| `PRIVACY_POLICY.md` | Required for Chrome Store |

### Modify Files
| File | Changes |
|------|---------|
| `extensions/UniversalShield/src/content.js` | Add API integration |
| `extensions/UniversalShield/src/background.js` | Add auth & quota |
| `extensions/UniversalShield/src/detector.js` | Add cloud ML fallback |
| `extensions/UniversalShield/popup/popup.html` | Add upgrade button |
| `extensions/UniversalShield/popup/popup.js` | Add tier logic |

---

## Testing Checklist

### Local Testing
- [ ] Extension loads without errors
- [ ] Scam patterns detected on LinkedIn
- [ ] Badges display correctly
- [ ] Popup shows stats
- [ ] Settings toggle works

### API Testing
- [ ] API responds to analyze-message
- [ ] Rate limiting works
- [ ] CORS allows extension requests
- [ ] SSL certificate valid

### Integration Testing
- [ ] Extension calls API for suspicious messages
- [ ] Fallback to local detection works
- [ ] Pro features gated correctly
- [ ] Payment flow works

---

## Success Metrics

| Metric | Target (30 days) |
|--------|------------------|
| Chrome Store installs | 500+ |
| Daily active users | 100+ |
| Scams blocked | 1,000+ |
| Pro conversions | 25+ ($125/mo) |
| API uptime | 99.9% |

---

## Notes

- **Do NOT add ads** - destroys trust for security product
- Keep Free tier valuable enough to attract users
- Pro tier should feel like a clear upgrade
- Focus on LinkedIn first, then expand to Gmail/Outlook
- Consider launching on Product Hunt for visibility

---

## Phase 7: PayPal Subscription Integration

### Overview
Use same PayPal Business account as NOMADA donations for UniversalShield Pro subscriptions.

### Task 7.1: Create PayPal Subscription Plan

**In PayPal Dashboard:**
1. Go to PayPal Business → Products & Services → Subscriptions
2. Create Product: "UniversalShield"
3. Create Plan: "Pro Monthly - $4.99/month"
4. Create Plan: "Pro Annual - $39/year"
5. Copy **Plan IDs** for integration

### Task 7.2: Create Payment Page

**File:** `web/upgrade.html` (hosted on your domain)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Upgrade to UniversalShield Pro</title>
  <script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&vault=true&intent=subscription"></script>
</head>
<body>
  <h1>🛡️ UniversalShield Pro</h1>
  
  <div id="paypal-button-monthly"></div>
  <div id="paypal-button-annual"></div>
  
  <script>
    // Monthly subscription
    paypal.Buttons({
      style: { label: 'subscribe' },
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          plan_id: 'P-XXXXXXXXXXXXXXXXXXXXXXXX' // Monthly plan ID
        });
      },
      onApprove: function(data, actions) {
        // Send subscription ID to your API
        fetch('https://api.universalshield.dev/api/v1/subscription/activate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subscription_id: data.subscriptionID,
            email: data.payerEmail
          })
        }).then(res => res.json())
          .then(data => {
            // Show license key to user
            alert('Your license key: ' + data.license_key);
          });
      }
    }).render('#paypal-button-monthly');
    
    // Annual subscription (same pattern with annual plan ID)
  </script>
</body>
</html>
```

### Task 7.3: Create Subscription API Endpoints

**File:** `src/api/subscription_api.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets
import httpx

router = APIRouter(prefix="/api/v1/subscription")

# PayPal API credentials (same account as NOMADA)
PAYPAL_CLIENT_ID = "your_client_id"
PAYPAL_SECRET = "your_secret"
PAYPAL_API = "https://api-m.paypal.com"  # Use sandbox for testing

class SubscriptionActivation(BaseModel):
    subscription_id: str
    email: str

class LicenseValidation(BaseModel):
    license_key: str

# In-memory store (use database in production)
licenses = {}

@router.post("/activate")
async def activate_subscription(data: SubscriptionActivation):
    """Verify PayPal subscription and generate license key"""
    
    # 1. Verify subscription with PayPal API
    async with httpx.AsyncClient() as client:
        # Get access token
        auth_response = await client.post(
            f"{PAYPAL_API}/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
            data={"grant_type": "client_credentials"}
        )
        access_token = auth_response.json()["access_token"]
        
        # Verify subscription
        sub_response = await client.get(
            f"{PAYPAL_API}/v1/billing/subscriptions/{data.subscription_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if sub_response.status_code != 200:
            raise HTTPException(400, "Invalid subscription")
        
        sub_data = sub_response.json()
        if sub_data["status"] != "ACTIVE":
            raise HTTPException(400, "Subscription not active")
    
    # 2. Generate license key
    license_key = f"US-PRO-{secrets.token_hex(8).upper()}"
    
    # 3. Store license (link to subscription)
    licenses[license_key] = {
        "subscription_id": data.subscription_id,
        "email": data.email,
        "tier": "pro",
        "active": True
    }
    
    return {
        "success": True,
        "license_key": license_key,
        "tier": "pro"
    }

@router.post("/validate")
async def validate_license(data: LicenseValidation):
    """Validate license key from extension"""
    
    if data.license_key not in licenses:
        return {"valid": False, "tier": "free"}
    
    license_info = licenses[data.license_key]
    
    # TODO: Check with PayPal if subscription still active
    
    return {
        "valid": license_info["active"],
        "tier": license_info["tier"]
    }

@router.post("/webhook")
async def paypal_webhook(payload: dict):
    """Handle PayPal subscription events (cancel, suspend, etc.)"""
    
    event_type = payload.get("event_type")
    resource = payload.get("resource", {})
    subscription_id = resource.get("id")
    
    if event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        # Find and deactivate license
        for key, info in licenses.items():
            if info["subscription_id"] == subscription_id:
                licenses[key]["active"] = False
                break
    
    return {"status": "ok"}
```

### Task 7.4: Update Extension for License Validation

**File:** `extensions/UniversalShield/src/license.js`

```javascript
const LICENSE_API = 'https://api.universalshield.dev/api/v1/subscription';

async function checkLicense() {
  const stored = await chrome.storage.sync.get(['license_key']);
  
  if (!stored.license_key) {
    return { valid: false, tier: 'free' };
  }
  
  try {
    const response = await fetch(`${LICENSE_API}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ license_key: stored.license_key })
    });
    
    return await response.json();
  } catch (error) {
    // Offline - trust cached license for 7 days
    const lastCheck = await chrome.storage.local.get(['license_last_check']);
    const daysSinceCheck = (Date.now() - lastCheck.license_last_check) / (1000 * 60 * 60 * 24);
    
    if (daysSinceCheck < 7) {
      return { valid: true, tier: 'pro', offline: true };
    }
    return { valid: false, tier: 'free' };
  }
}

async function saveLicense(licenseKey) {
  await chrome.storage.sync.set({ license_key: licenseKey });
  await chrome.storage.local.set({ license_last_check: Date.now() });
}

async function openUpgradePage() {
  chrome.tabs.create({ url: 'https://universalshield.dev/upgrade' });
}
```

### Task 7.5: Add Upgrade Button to Popup

**File:** `extensions/UniversalShield/popup/popup.html` (add before footer)

```html
<section class="upgrade-section" id="upgradeSection">
  <h3>⭐ Upgrade to Pro</h3>
  <ul>
    <li>✅ Unlimited scans</li>
    <li>✅ Cloud ML analysis</li>
    <li>✅ Gmail & Outlook</li>
    <li>✅ Fraud ring detection</li>
  </ul>
  <button class="upgrade-btn" id="upgradeBtn">
    Upgrade - $4.99/mo
  </button>
  <p class="license-input" id="licenseInput" style="display:none;">
    <input type="text" id="licenseKey" placeholder="Enter license key">
    <button id="activateBtn">Activate</button>
  </p>
</section>
```

**File:** `extensions/UniversalShield/popup/popup.js` (add)

```javascript
// Check license on popup open
document.addEventListener('DOMContentLoaded', async () => {
  const license = await checkLicense();
  
  if (license.valid && license.tier === 'pro') {
    document.getElementById('upgradeSection').innerHTML = `
      <div class="pro-badge">⭐ Pro Active</div>
    `;
  }
});

// Upgrade button click
document.getElementById('upgradeBtn').addEventListener('click', () => {
  openUpgradePage();
});

// Show license input
document.getElementById('upgradeBtn').addEventListener('contextmenu', (e) => {
  e.preventDefault();
  document.getElementById('licenseInput').style.display = 'block';
});

// Activate license
document.getElementById('activateBtn').addEventListener('click', async () => {
  const key = document.getElementById('licenseKey').value;
  if (key) {
    await saveLicense(key);
    location.reload();
  }
});
```

### PayPal Setup Checklist

- [ ] Same PayPal Business account as NOMADA
- [ ] Create "UniversalShield" product in PayPal
- [ ] Create Monthly plan ($4.99)
- [ ] Create Annual plan ($39)
- [ ] Copy Plan IDs to code
- [ ] Set up webhook URL in PayPal
- [ ] Test with PayPal Sandbox first
- [ ] Switch to Live when ready

### PayPal Fees

| Plan | Price | PayPal Fee (~3.5%) | You Keep |
|------|-------|-------------------|----------|
| Monthly | $4.99 | $0.17 | $4.82 |
| Annual | $39 | $1.37 | $37.63 |

---

## Commands Reference

```bash
# Start API locally
cd /Users/jcubero/ParadigmStore/agents/paradigm.fraud.agent
uvicorn src.api.scam_detection_api:app --reload --port 8000

# Test extension
# chrome://extensions/ → Load unpacked → extensions/UniversalShield

# Push changes
git add . && git commit -m "message" && git push

# Deploy to VPS (after setup)
ssh user@vps "cd universalshield && git pull && systemctl restart universalshield"
```

---

**Created:** January 9, 2026  
**Author:** Cascade + jcubero  
**Status:** Ready for implementation
