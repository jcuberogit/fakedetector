# UniversalShield Architecture

> **CRITICAL PRINCIPLE**: The VPS Fraud Agent (IA) is the BRAIN. The extension is merely a SENSOR.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER'S BROWSER                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    UniversalShield Extension                         │    │
│  │                        (THIN CLIENT)                                 │    │
│  │                                                                      │    │
│  │  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │    │
│  │  │ content.js   │───►│ FeatureExtractor │───►│ CloudAnalyzer   │   │    │
│  │  │ (DOM Sensor) │    │ (Anonymizer)     │    │ (API Client)    │   │    │
│  │  └──────────────┘    └──────────────────┘    └────────┬────────┘   │    │
│  │         ▲                                              │            │    │
│  │         │ Display Result                               │            │    │
│  │         │                                              │            │    │
│  │  ┌──────┴──────┐                                       │            │    │
│  │  │ UI Badge +  │◄──────────────────────────────────────┘            │    │
│  │  │ Tooltip     │         VPS Agent Verdict                          │    │
│  │  └─────────────┘                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS (anonymized features ONLY)
                                    │ Never raw message content
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        api.tucan.store (VPS)                                 │
│                         FRAUD AGENT (IA)                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐  │    │
│  │  │ scam_detection   │───►│ MLService        │───►│ XGBoost      │  │    │
│  │  │ _api.py          │    │ (Prediction)     │    │ Model        │  │    │
│  │  │ (FastAPI)        │    └──────────────────┘    └──────────────┘  │    │
│  │  └────────┬─────────┘                                               │    │
│  │           │                                                         │    │
│  │           ▼                                                         │    │
│  │  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐  │    │
│  │  │ Feedback Loop    │───►│ PostgreSQL       │───►│ Weekly       │  │    │
│  │  │ /report-scam     │    │ training_feedback│    │ Retraining   │  │    │
│  │  └──────────────────┘    └──────────────────┘    └──────────────┘  │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📍 What Lives Where

### Extension (Thin Client) - ONLY:
| Component | Responsibility |
|-----------|----------------|
| `content.js` | Find message DOM elements, trigger scan |
| `FeatureExtractor` | Convert text → anonymized numerical features |
| `CloudAnalyzer` | Send features to VPS, receive verdict |
| `UI (Badge/Tooltip)` | Display VPS Agent's verdict to user |
| `reportScam()` | Send feedback to VPS for ML growth |

### VPS Agent (The Brain) - ALL DETECTION:
| Component | Responsibility |
|-----------|----------------|
| `scam_detection_api.py` | API endpoints, rate limiting, license validation |
| `MLService` | XGBoost model prediction |
| `PrivacyFirstFeatureExtractor` | Server-side feature validation |
| `PostgreSQL` | Store feedback for retraining |
| `retrain_job.py` | Weekly model retraining |
| `GNN Service` | Fraud ring detection (Pro only) |

## ❌ What NEVER Goes in Extension

- Regex patterns for scam detection
- Scoring logic
- Risk level determination
- Pattern matching rules
- ANY detection authority

## 🔒 Privacy Guarantee

The extension NEVER sends raw message content to the VPS. Only anonymized numerical features:

```json
{
  "message_length": 450,
  "word_count": 87,
  "urgency_keywords_count": 3,
  "money_keywords_count": 2,
  "sender_account_age_days": 14,
  "connection_degree": 3,
  "platform_id": 1,
  "requests_payment": 1,
  "has_urgency": 1
}
```

## 💰 Monetization Tiers

| Feature | Free | Pro |
|---------|------|-----|
| Scans per day | 50 | Unlimited |
| Risk Score | ✅ | ✅ |
| Risk Level | ✅ | ✅ |
| AI Explanation | ❌ | ✅ |
| ML Confidence | ❌ | ✅ |
| Fraud Ring Detection | ❌ | ✅ |
| All Platforms | ❌ | ✅ |

## 🔄 Feedback Loop for ML Growth

```
User clicks "Report Scam" or "False Positive"
           │
           ▼
Extension sends features + label to /api/v1/report-scam
           │
           ▼
VPS stores in PostgreSQL training_feedback table
           │
           ▼
Weekly cron job runs retrain_job.py
           │
           ▼
New XGBoost model trained on expanded dataset
           │
           ▼
Model deployed, Agent gets smarter
```

## 🚨 Architecture Violations to Watch For

1. **Adding regex patterns to extension** → VIOLATION
2. **Local scoring in content.js** → VIOLATION
3. **Math.max(local, cloud) combination** → VIOLATION
4. **Fallback to local detection** → VIOLATION
5. **Detection logic outside VPS** → VIOLATION

## 📋 Reference Files

- Extension: `extensions/src/content.js`, `extensions/src/cloudAnalyzer.js`
- VPS API: `src/api/scam_detection_api.py`
- ML: `src/ml/ml_service.py`
- Tickets: `UniversalShield-Tickets.csv`

---

**Last Updated**: 2026-01-10
**Maintained By**: Opus Architecture Review
