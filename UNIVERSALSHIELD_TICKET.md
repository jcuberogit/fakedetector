# UniversalShield Implementation Ticket

## Project Overview
**Repo:** https://github.com/jcuberogit/universalshield  
**Status:** Extension working locally, needs API integration  
**Priority:** High  
**Estimated Time:** 5-7 weeks (MVP)  

---

## 🎯 The "NOMADA Edge" - Technical Differentiators

### 1. Contextual Intelligence (NOT Just Blacklists)

**Problem with competitors:** Normal extensions fail because scammers change URLs hourly. Blacklists are always outdated.

**Our solution:** UniversalShield analyzes **semantics and behavior context**, not just links.

**Example:**
```
Scenario: "Recruiter" on LinkedIn asks you to download assessment.exe for interview

Traditional Detection (FAILS):
✗ URL not in blacklist
✗ Keywords "congrats", "opening" are normal
→ Marked as SAFE ❌

UniversalShield Contextual Analysis (DETECTS):
✓ Platform: LinkedIn (professional context)
✓ Sender claim: Recruiter
✓ Account age: 2 days (suspicious)
✓ Action requested: Download .exe (dangerous in professional context)
✓ Urgency: "Need it today" (pressure tactic)
✓ Connection: 3rd degree (no relationship)
✓ Pattern: Classic social engineering
→ RISK SCORE: 95/100 🔴
```

### 2. Zero-Latency Privacy (Privacy-First Architecture)

**Principle:** A security product that violates privacy is a contradiction.

**Architecture:**
```
FREE TIER (100% Local):
├── All analysis happens in browser
├── Zero bytes sent to any server
├── Pattern matching + basic context scoring
└── Response time: <10ms

PRO TIER (Anonymized Features Only):
├── Extracts numerical features locally
├── Sends ONLY anonymized feature vectors
├── NO message content sent
├── NO personal data collected
├── E2E encryption for all transmissions
└── Zero retention policy on server
```

**What PRO tier sends (anonymized features):**
```json
{
  "features": {
    "message_length": 450,
    "urgency_keywords_count": 3,
    "link_count": 1,
    "file_attachment": true,
    "file_extension_risk": 0.95,
    "sender_account_age_days": 2,
    "connection_degree": 3,
    "platform": "linkedin",
    "context_type": "recruitment"
  }
}
```

**What is NEVER sent:**
- ❌ Message content
- ❌ Names or personal identifiers
- ❌ Email addresses
- ❌ Specific URLs
- ❌ Any PII

### 3. Visual Badges & Frictionless UX

**3-Tier Color System:**
```
🟢 GREEN (risk_score < 30): Safe
   └── No interruption, message displays normally

🟡 YELLOW (risk_score 30-70): Caution
   └── "⚠️ Heads up: New account, urgency detected"
   └── User can continue but is informed

🔴 RED (risk_score > 70): Critical Risk
   └── "🛑 SCAM DETECTED: Pattern matches social engineering"
   └── Detailed explanation + Report button
```

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
- [ ] Contextual Intelligence Engine
- [ ] Privacy-First anonymization layer
- [ ] Extension not connected to fraud agent API
- [ ] No VPS deployment
- [ ] No cloud ML analysis
- [ ] No GNN fraud ring detection
- [ ] No user authentication
- [ ] Not on Chrome Web Store

---

## Implementation Tasks

### Phase 0: Proof of Concept (Week 1)

#### Task 0.1: Validate Contextual Intelligence
- Create 20 real scam examples from LinkedIn/Gmail
- Implement basic contextual analyzer
- Test detection precision (target: >85%)
- Adjust LLM prompts for optimal detection

#### Task 0.2: Define Feature Extraction Schema
```python
# Anonymized features to extract (no PII)
FEATURE_SCHEMA = {
    'behavioral': {
        'platform': str,           # linkedin, gmail, outlook
        'action_requested': str,   # download, click, transfer, etc.
        'file_type': str,          # exe, pdf, none, etc.
        'link_count': int,
        'urgency_level': float,    # 0-1 score
    },
    'social': {
        'sender_account_age_days': int,
        'connection_degree': int,  # 1st, 2nd, 3rd
        'previous_interactions': int,
        'claimed_role': str,       # recruiter, investor, etc.
    },
    'linguistic': {
        'message_length': int,
        'urgency_keywords': int,
        'money_keywords': int,
        'personal_info_requests': int,
    }
}
```

---

### Phase 1: Contextual Analysis Engine (Week 2)

#### Task 1.1: Build Contextual Analyzer
**File:** `src/contextual/analyzer.py`

```python
class ContextualAnalyzer:
    """
    Analyzes messages using multi-dimensional context,
    NOT just keywords or blacklists.
    """
    
    def analyze(self, message: str, metadata: dict) -> dict:
        # Extract context signals
        context = {
            'behavioral': self._analyze_behavior(message, metadata),
            'social': self._analyze_social_signals(metadata),
            'temporal': self._analyze_timing(metadata),
            'linguistic': self._analyze_language(message)
        }
        
        # Calculate contextual risk score
        risk_score = self._calculate_contextual_risk(context)
        
        # Generate human-readable explanation
        explanation = self._generate_explanation(context, risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'context_signals': context,
            'explanation': explanation,
            'recommended_action': self._get_action(risk_score)
        }
    
    def _analyze_behavior(self, message, metadata):
        return {
            'platform': metadata.get('platform'),
            'action_requested': self._detect_action(message),  # download, click, transfer
            'file_type': self._detect_file_type(message),
            'link_count': self._count_links(message),
            'urgency_level': self._calculate_urgency(message)
        }
    
    def _analyze_social_signals(self, metadata):
        return {
            'account_age_days': metadata.get('sender_account_age', 0),
            'connection_degree': metadata.get('connection_degree', 3),
            'claimed_role': self._detect_claimed_role(metadata),
            'previous_interactions': metadata.get('previous_interactions', 0)
        }
    
    def _get_risk_level(self, score):
        if score < 30: return 'safe'      # 🟢 GREEN
        if score < 70: return 'caution'   # 🟡 YELLOW
        return 'critical'                  # 🔴 RED
```

#### Task 1.2: Build Feature Extractor (Privacy Layer)
**File:** `src/contextual/feature_extractor.py`

```python
class PrivacyFirstFeatureExtractor:
    """
    Extracts ONLY anonymized numerical features.
    NO message content, NO PII ever leaves the browser.
    """
    
    def extract_features(self, message: str, metadata: dict) -> dict:
        # Returns ONLY numerical/categorical features
        # NEVER raw text or PII
        return {
            'message_length': len(message),
            'urgency_keywords_count': self._count_urgency_keywords(message),
            'money_keywords_count': self._count_money_keywords(message),
            'link_count': len(re.findall(r'https?://', message)),
            'file_attachment': bool(metadata.get('has_attachment')),
            'file_extension_risk': self._get_extension_risk(metadata),
            'sender_account_age_days': metadata.get('account_age', 0),
            'connection_degree': metadata.get('connection', 3),
            'platform_id': self._platform_to_id(metadata.get('platform')),
            'context_type_id': self._context_to_id(metadata.get('context'))
        }
    
    # PRIVACY GUARANTEE: These features are:
    # ✅ Anonymized (no way to reconstruct original message)
    # ✅ Numerical (no strings that could contain PII)
    # ✅ Aggregated (counts, not content)
```

#### Task 1.3: Create REST API Endpoints
**File:** `src/api/scam_detection_api.py`

```python
# Privacy-First API Endpoints:

POST /api/v1/analyze-features
  - Input: { features: {...} }  # ONLY anonymized features, NOT message content
  - Output: { risk_score, risk_level, explanation }

POST /api/v1/report-pattern
  - Input: { pattern_hash, category }  # Hashed pattern, no raw content
  - Output: { success, pattern_id }

GET /api/v1/patterns/latest
  - Output: { patterns, version, updated_at }

POST /api/v1/subscription/validate
  - Input: { license_key }
  - Output: { valid, tier, features_enabled }
```

#### Task 1.4: Add CORS & Security
- Allow requests from Chrome extension only
- Rate limiting: Free 50/day, Pro unlimited
- E2E encryption for all API calls
- Zero-retention logging (no request bodies stored)

---

### Phase 2: Privacy-First Architecture (Week 3)

#### Task 2.1: Implement Local-First Analysis (FREE Tier)
**File:** `extensions/UniversalShield/src/localAnalyzer.js`

```javascript
/**
 * FREE TIER: 100% local analysis
 * ZERO data sent to any server
 */
class LocalAnalyzer {
  constructor() {
    this.patterns = SCAM_PATTERNS; // 100+ patterns bundled
  }
  
  analyze(message, metadata) {
    // All analysis happens in browser
    const behavioral = this.analyzeBehavior(message, metadata);
    const linguistic = this.analyzeLinguistic(message);
    const social = this.analyzeSocial(metadata);
    
    const riskScore = this.calculateRisk(behavioral, linguistic, social);
    
    return {
      risk_score: riskScore,
      risk_level: this.getRiskLevel(riskScore),
      explanation: this.generateExplanation(behavioral, linguistic, social),
      source: 'local' // Indicates no server call was made
    };
  }
  
  getRiskLevel(score) {
    if (score < 30) return 'safe';      // 🟢
    if (score < 70) return 'caution';   // 🟡
    return 'critical';                   // 🔴
  }
}
```

#### Task 2.2: Implement Cloud Analysis (PRO Tier)
**File:** `extensions/UniversalShield/src/cloudAnalyzer.js`

```javascript
/**
 * PRO TIER: Enhanced ML analysis
 * Sends ONLY anonymized features (never raw content)
 */
class CloudAnalyzer {
  constructor(apiUrl, licenseKey) {
    this.apiUrl = apiUrl;
    this.licenseKey = licenseKey;
    this.featureExtractor = new FeatureExtractor();
  }
  
  async analyze(message, metadata) {
    // Step 1: Extract anonymized features LOCALLY
    const features = this.featureExtractor.extract(message, metadata);
    
    // Step 2: Send ONLY features to API (never raw message)
    // Privacy guarantee: features cannot be used to reconstruct message
    const response = await fetch(`${this.apiUrl}/api/v1/analyze-features`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-License-Key': this.licenseKey
      },
      body: JSON.stringify({ features }) // NO message content!
    });
    
    return await response.json();
  }
}

class FeatureExtractor {
  extract(message, metadata) {
    // Returns ONLY numerical features - NEVER raw text
    return {
      message_length: message.length,
      urgency_keywords_count: this.countUrgencyKeywords(message),
      money_keywords_count: this.countMoneyKeywords(message),
      link_count: (message.match(/https?:\/\//g) || []).length,
      file_attachment: !!metadata.hasAttachment,
      file_extension_risk: this.getExtensionRisk(metadata.fileType),
      sender_account_age_days: metadata.accountAge || 0,
      connection_degree: metadata.connectionDegree || 3,
      platform_id: this.platformToId(metadata.platform)
    };
  }
}
```

#### Task 2.3: VPS Deployment
**Provider:** Hetzner ($10/mo - best price/performance)

```bash
# On VPS:
git clone https://github.com/jcuberogit/universalshield.git
cd universalshield
pip install -r requirements.txt

# Configure zero-retention logging
export LOG_LEVEL=WARNING  # No request body logging
export DATA_RETENTION=0   # Zero retention policy

# Start API server
uvicorn src.api.scam_detection_api:app --host 0.0.0.0 --port 8000
```

#### Task 2.4: Setup Domain & SSL
- Domain: `api.universalshield.dev`
- SSL: Let's Encrypt (free, auto-renewal)
- Security headers: HSTS, CSP, X-Content-Type-Options

#### Task 2.5: Nginx with Privacy Headers
```nginx
server {
    listen 443 ssl http2;
    server_name api.universalshield.dev;
    
    # SSL
    ssl_certificate /etc/letsencrypt/live/api.universalshield.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.universalshield.dev/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    
    # ZERO request body logging (privacy)
    access_log /var/log/nginx/access.log combined;  # No body
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Phase 3: Visual Badge System (Week 4)

#### Task 3.1: Implement 3-Tier Badge Component
**File:** `extensions/UniversalShield/src/badge.js`

```javascript
/**
 * Visual Badge System - Frictionless UX
 * 
 * 🟢 GREEN: Safe (score < 30) - No interruption
 * 🟡 YELLOW: Caution (score 30-70) - Subtle warning
 * 🔴 RED: Critical (score > 70) - Clear alert
 */
class ShieldBadge {
  constructor() {
    this.container = null;
  }
  
  render(analysis, messageElement) {
    const badge = document.createElement('div');
    badge.className = `universalshield-badge ${analysis.risk_level}`;
    
    badge.innerHTML = `
      <span class="shield-icon">${this.getIcon(analysis.risk_level)}</span>
      <span class="risk-label">${this.getLabel(analysis.risk_level)}</span>
      <button class="details-btn" title="Why?">?</button>
    `;
    
    // Position badge near message
    messageElement.style.position = 'relative';
    messageElement.appendChild(badge);
    
    // Add click handler for explanation
    badge.querySelector('.details-btn').addEventListener('click', () => {
      this.showExplanation(analysis);
    });
    
    return badge;
  }
  
  getIcon(level) {
    const icons = {
      'safe': '🛡️',
      'caution': '⚠️',
      'critical': '🚨'
    };
    return icons[level] || '🛡️';
  }
  
  getLabel(level) {
    const labels = {
      'safe': 'Safe',
      'caution': 'Caution',
      'critical': 'RISK'
    };
    return labels[level] || 'Unknown';
  }
  
  showExplanation(analysis) {
    const modal = document.createElement('div');
    modal.className = 'universalshield-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>${this.getIcon(analysis.risk_level)} Risk Analysis</h3>
        <div class="risk-score">
          <span class="score">${analysis.risk_score}</span>/100
        </div>
        <div class="explanation">
          ${this.formatExplanation(analysis.explanation)}
        </div>
        <div class="signals">
          <h4>Detected Signals:</h4>
          <ul>
            ${this.formatSignals(analysis.context_signals)}
          </ul>
        </div>
        <div class="actions">
          <button class="report-btn">🚩 Report Scam</button>
          <button class="dismiss-btn">Dismiss</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    modal.querySelector('.dismiss-btn').addEventListener('click', () => {
      modal.remove();
    });
    
    modal.querySelector('.report-btn').addEventListener('click', () => {
      this.reportScam(analysis);
      modal.remove();
    });
  }
  
  formatSignals(signals) {
    const items = [];
    
    if (signals.behavioral?.urgency_level > 0.7) {
      items.push('<li class="warning">⚡ High urgency language detected</li>');
    }
    if (signals.social?.account_age_days < 30) {
      items.push('<li class="warning">👤 New account (less than 30 days)</li>');
    }
    if (signals.behavioral?.file_type === 'exe') {
      items.push('<li class="danger">📁 Executable file attachment</li>');
    }
    if (signals.social?.connection_degree > 2) {
      items.push('<li class="warning">🔗 No direct connection</li>');
    }
    
    return items.join('');
  }
}
```

#### Task 3.2: Badge Styles (CSS)
**File:** `extensions/UniversalShield/src/badge.css`

```css
/* Base badge styles */
.universalshield-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1000;
}

/* 🟢 SAFE - Minimal, non-intrusive */
.universalshield-badge.safe {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

/* 🟡 CAUTION - Visible but not alarming */
.universalshield-badge.caution {
  background: rgba(251, 191, 36, 0.15);
  color: #d97706;
  border: 1px solid rgba(251, 191, 36, 0.3);
  animation: pulse-yellow 2s infinite;
}

/* 🔴 CRITICAL - Clear danger signal */
.universalshield-badge.critical {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
  border: 2px solid #dc2626;
  animation: pulse-red 1s infinite;
}

@keyframes pulse-yellow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.4); }
  50% { box-shadow: 0 0 0 4px rgba(251, 191, 36, 0); }
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
  50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
}

/* Modal styles */
.universalshield-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.universalshield-modal .modal-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.universalshield-modal .risk-score {
  font-size: 48px;
  font-weight: bold;
  text-align: center;
  margin: 16px 0;
}

.universalshield-modal .signals li.warning {
  color: #d97706;
}

.universalshield-modal .signals li.danger {
  color: #dc2626;
  font-weight: bold;
}
```

#### Task 3.3: Update Content Script Integration
**File:** `extensions/UniversalShield/src/content.js`

```javascript
// Integration with badge system
async function analyzeAndBadge(messageElement, messageText, metadata) {
  const tier = await getLicenseTier();
  let analysis;
  
  if (tier === 'pro') {
    // PRO: Cloud ML with anonymized features
    analysis = await cloudAnalyzer.analyze(messageText, metadata);
  } else {
    // FREE: 100% local analysis
    analysis = localAnalyzer.analyze(messageText, metadata);
  }
  
  // Only show badge if risk detected (don't clutter safe messages)
  if (analysis.risk_score >= 30) {
    const badge = new ShieldBadge();
    badge.render(analysis, messageElement);
  }
  
  // Update stats
  chrome.runtime.sendMessage({
    type: 'UPDATE_STATS',
    data: { 
      scanned: 1, 
      blocked: analysis.risk_score >= 70 ? 1 : 0 
    }
  });
}
```

---

### Phase 4: ML Integration (Week 5)

#### Task 4.1: Connect to Fraud Agent ML Services
**File:** `src/api/ml_endpoint.py`

```python
from fastapi import APIRouter
from src.ml_service import MLService
from src.gnn_service import GNNService
from src.rules_engine_service import RulesEngineService

router = APIRouter(prefix="/api/v1/ml")

ml_service = MLService()
gnn_service = GNNService()
rules_engine = RulesEngineService()

@router.post("/analyze")
async def analyze_features(features: dict):
    """
    Analyze ANONYMIZED features only.
    NO message content ever reaches this endpoint.
    """
    # XGBoost prediction on features
    ml_score = ml_service.predict_risk(features)
    
    # Rules engine for known patterns
    rules_score = rules_engine.evaluate(features)
    
    # Combine scores with weights
    final_score = (ml_score * 0.6) + (rules_score * 0.4)
    
    return {
        'risk_score': round(final_score * 100),
        'ml_confidence': ml_service.get_confidence(),
        'patterns_matched': rules_engine.get_matched_patterns()
    }

@router.post("/fraud-ring")  # PRO only
async def detect_fraud_ring(features: dict, sender_hash: str):
    """
    GNN-based fraud ring detection.
    Uses hashed sender ID, never real identity.
    """
    ring_probability = gnn_service.detect_ring(sender_hash, features)
    
    return {
        'fraud_ring_probability': ring_probability,
        'ring_size_estimate': gnn_service.estimate_ring_size()
    }
```

#### Task 4.2: Train Scam Detection Model
**Input features (all anonymized):**
- `message_length`: int
- `urgency_keywords_count`: int
- `money_keywords_count`: int
- `link_count`: int
- `file_extension_risk`: float (0-1)
- `sender_account_age_days`: int
- `connection_degree`: int (1-3)
- `platform_id`: int
- `context_type_id`: int

**Output:**
- `risk_score`: 0-100
- `risk_level`: safe | caution | critical
- `explanation`: Human-readable reason
- `confidence`: 0-1

#### Task 4.3: Model Training Pipeline
```python
# Training data: Anonymized features from reported scams
# NO raw message content in training data

from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import joblib

def train_model(features_df, labels):
    X_train, X_test, y_train, y_test = train_test_split(
        features_df, labels, test_size=0.2
    )
    
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1
    )
    
    model.fit(X_train, y_train)
    
    # Target: >85% precision, >80% recall
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy}")
    
    joblib.dump(model, 'models/scam_detector_v1.pkl')
    return model
```

---

### Phase 5: Freemium Implementation (Week 6)

#### Task 5.1: User Tiers with Privacy Focus
```javascript
const TIERS = {
  FREE: {
    name: 'Free',
    dailyScans: 50,
    analysisType: 'local',        // 100% private, no server calls
    cloudML: false,
    platforms: ['linkedin'],
    fraudRingDetection: false,
    privacy: '100% local - zero data sent'
  },
  PRO: {
    name: 'Pro',
    dailyScans: Infinity,
    analysisType: 'cloud',        // Anonymized features only
    cloudML: true,
    platforms: ['linkedin', 'gmail', 'outlook'],
    fraudRingDetection: true,
    price: 4.99,                  // monthly
    annualPrice: 39,              // yearly (35% off)
    privacy: 'Anonymized features only - zero PII'
  }
};
```

#### Task 5.2: Feature Comparison Display
```javascript
const FEATURE_COMPARISON = {
  'Daily Scans': { free: '50', pro: 'Unlimited' },
  'Analysis': { free: 'Local patterns', pro: 'Cloud ML + GNN' },
  'Platforms': { free: 'LinkedIn', pro: 'LinkedIn, Gmail, Outlook' },
  'Fraud Ring Detection': { free: '❌', pro: '✅' },
  'Contextual Intelligence': { free: 'Basic', pro: 'Advanced AI' },
  'Privacy': { free: '100% Local', pro: 'Anonymized Features Only' }
};
```

#### Task 5.3: License Key System
- Generate secure license keys: `US-PRO-{random_hex}`
- Validate against PayPal subscription status
- Cache locally for offline use (7 day grace period)
- Store in chrome.storage.sync (syncs across devices)

---

### Phase 6: PayPal Subscription Integration (Week 6)

#### Task 6.1: Create PayPal Subscription Plans
**In PayPal Dashboard (same account as NOMADA):**
1. Go to PayPal Business → Products & Services → Subscriptions
2. Create Product: "UniversalShield"
3. Create Plan: "Pro Monthly - $4.99/month"
4. Create Plan: "Pro Annual - $39/year"
5. Copy **Plan IDs** for integration

#### Task 6.2: Subscription API Endpoints
**File:** `src/api/subscription_api.py`

```python
@router.post("/activate")
async def activate_subscription(data: SubscriptionActivation):
    """Verify PayPal subscription and generate license key"""
    # 1. Verify with PayPal API
    # 2. Generate license: US-PRO-{random_hex}
    # 3. Return license key to user
    
@router.post("/validate")
async def validate_license(data: LicenseValidation):
    """Validate license key from extension"""
    # Check license exists and subscription active
    
@router.post("/webhook")
async def paypal_webhook(payload: dict):
    """Handle subscription cancellation/suspension"""
```

#### Task 6.3: PayPal Fees
| Plan | Price | PayPal Fee (~3.5%) | You Keep |
|------|-------|-------------------|----------|
| Monthly | $4.99 | $0.17 | $4.82 |
| Annual | $39 | $1.37 | $37.63 |

---

### Phase 7: Chrome Web Store Submission (Week 7)

#### Task 7.1: Prepare Assets
- [ ] 128x128 icon (PNG)
- [ ] 440x280 small promo tile
- [ ] 1280x800 large promo tile
- [ ] 5 screenshots (1280x800)
- [ ] Privacy policy URL (emphasize zero-data-retention)
- [ ] Detailed description highlighting privacy-first approach

#### Task 7.2: Privacy Policy (Key Points)
**File:** `PRIVACY_POLICY.md`

```markdown
# UniversalShield Privacy Policy

## Our Privacy Commitment

UniversalShield is designed with **Privacy-First** architecture:

### FREE Tier
- ✅ 100% local analysis
- ✅ Zero data sent to any server
- ✅ No tracking, no analytics
- ✅ Works completely offline

### PRO Tier
- ✅ Only anonymized numerical features sent
- ✅ NO message content transmitted
- ✅ NO personal information collected
- ✅ Zero retention policy (data not stored)
- ✅ E2E encryption for all transmissions

### What We NEVER Collect
- ❌ Message content
- ❌ Names or personal identifiers
- ❌ Email addresses
- ❌ Browsing history
- ❌ Any personally identifiable information (PII)

### Data Flow (PRO Tier Only)
1. Message analyzed locally in your browser
2. Only numerical features extracted (message_length, keyword_counts, etc.)
3. Features cannot be used to reconstruct original message
4. Server returns risk score, no data stored
```

#### Task 7.3: Developer Account & Submission
- Create Google Developer account ($5 one-time fee)
- Verify identity
- Submit extension for review (1-3 days)
- Prepare justification for permissions:
  - `activeTab`: Required to scan messages on current page
  - `storage`: Store user preferences and license key
  - `host_permissions`: Access LinkedIn/Gmail/Outlook pages

---

## Roadmap Summary

| Phase | Description | Week | Status |
|-------|-------------|------|--------|
| **Phase 0** | Proof of Concept - Validate Contextual Intelligence | Week 1 | ⏳ Pending |
| **Phase 1** | Contextual Analysis Engine | Week 2 | ⏳ Pending |
| **Phase 2** | Privacy-First Architecture | Week 3 | ⏳ Pending |
| **Phase 3** | Visual Badge System | Week 4 | ⏳ Pending |
| **Phase 4** | ML Integration | Week 5 | ⏳ Pending |
| **Phase 5** | Freemium Implementation | Week 6 | ⏳ Pending |
| **Phase 6** | PayPal Subscription | Week 6 | ⏳ Pending |
| **Phase 7** | Chrome Web Store | Week 7 | ⏳ Pending |

**Total Estimated Time: 7 weeks for MVP**

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
