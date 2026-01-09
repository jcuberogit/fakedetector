# UniversalShield Privacy Policy

**Last Updated:** January 9, 2026

## Our Privacy Commitment

UniversalShield is designed with **Privacy-First** architecture. We believe that a security product that violates privacy is a contradiction. This policy explains exactly what data we collect, how we use it, and what we NEVER collect.

---

## FREE Tier - 100% Local Analysis

### What Happens:
- ✅ **All analysis happens in your browser**
- ✅ **Zero bytes sent to any server**
- ✅ **No tracking, no analytics**
- ✅ **Works completely offline**
- ✅ **No account required**

### Data Collection:
- **NONE** - Absolutely zero data leaves your device

---

## PRO Tier - Anonymized Features Only

### What We Send to Our Server:
When you use PRO tier features, we send **ONLY anonymized numerical features** extracted locally in your browser. These features are:

- Message length (number)
- Keyword counts (numbers)
- Link count (number)
- File type risk score (number 0-1)
- Account age in days (number)
- Connection degree (number 1-3)
- Platform ID (categorical number)

### Privacy Guarantee:
These features **CANNOT be used to reconstruct your original message**. They are purely statistical signals.

### Example of What We Send:
```json
{
  "message_length": 450,
  "urgency_keywords_count": 3,
  "link_count": 1,
  "file_extension_risk": 0.95,
  "sender_account_age_days": 2,
  "connection_degree": 3,
  "platform_id": 1
}
```

### What We Return:
- Risk score (0-100)
- Risk level (safe/caution/critical)
- Explanation of why

### Data Retention:
- **ZERO retention policy**
- We do not store any request data
- Server logs contain only timestamps and status codes (no request bodies)

---

## What We NEVER Collect

We will **NEVER** collect, store, or transmit:

- ❌ **Message content** (the actual text of messages)
- ❌ **Names** or personal identifiers
- ❌ **Email addresses**
- ❌ **Phone numbers**
- ❌ **Specific URLs** you visit
- ❌ **Browsing history**
- ❌ **IP addresses** (not logged)
- ❌ **Any personally identifiable information (PII)**

---

## Data Flow Diagram

### FREE Tier:
```
Message → Local Analysis → Risk Score → Display Badge
(Everything stays in your browser)
```

### PRO Tier:
```
Message → Extract Features Locally → Send Features Only → 
Server Analyzes Features → Return Risk Score → Display Badge
(Original message NEVER leaves your browser)
```

---

## Permissions We Request

### Chrome Extension Permissions:

1. **`activeTab`**
   - **Why:** To scan messages on the current page (LinkedIn, Gmail, Outlook)
   - **What we do:** Read message content locally for analysis
   - **What we DON'T do:** Send message content to servers

2. **`storage`**
   - **Why:** Store your preferences and license key
   - **What we store:** Settings, license key, local stats
   - **What we DON'T store:** Message content or personal data

3. **`host_permissions`** (linkedin.com, gmail.com, outlook.com)
   - **Why:** Access these specific sites to provide protection
   - **What we do:** Inject our protection scripts
   - **What we DON'T do:** Track your activity or collect data

---

## Third-Party Services

### PayPal (Payment Processing Only):
- Used only for subscription payments
- We receive: Subscription ID, email (for license generation)
- We do NOT receive: Credit card details, full payment information
- PayPal's privacy policy applies: https://www.paypal.com/privacy

### No Other Third Parties:
- We do NOT use Google Analytics
- We do NOT use advertising networks
- We do NOT sell data to anyone
- We do NOT share data with anyone

---

## Your Rights

### You Have the Right To:
1. **Use the FREE tier forever** with zero data collection
2. **Request deletion** of your license key at any time
3. **Export your data** (though we store almost nothing)
4. **Cancel your subscription** anytime without penalty

### How to Exercise Your Rights:
- Email: privacy@universalshield.dev
- We will respond within 48 hours

---

## Security Measures

### How We Protect Your Data:

1. **E2E Encryption:** All API communications use HTTPS/TLS
2. **No Logs:** Server logs do not contain request bodies
3. **Minimal Storage:** We only store license keys (hashed)
4. **Regular Audits:** Code is open-source and auditable
5. **Secure Infrastructure:** VPS with security hardening

---

## Children's Privacy

UniversalShield is not directed at children under 13. We do not knowingly collect data from children.

---

## Changes to This Policy

We will notify users of any material changes via:
- Extension update notes
- Email (if you're a PRO subscriber)
- Website announcement

---

## Compliance

### GDPR (EU):
- ✅ Data minimization (we collect almost nothing)
- ✅ Purpose limitation (only for scam detection)
- ✅ Right to erasure (delete license anytime)
- ✅ Data portability (export available)

### CCPA (California):
- ✅ Right to know (this policy)
- ✅ Right to delete (email us)
- ✅ Right to opt-out (use FREE tier)
- ✅ No sale of personal information (we don't sell anything)

---

## Contact Us

**Privacy Questions:**
- Email: privacy@universalshield.dev
- Website: https://universalshield.dev/privacy

**General Support:**
- Email: support@universalshield.dev

---

## Summary (TL;DR)

**FREE Tier:**
- 100% local, zero data sent ✅

**PRO Tier:**
- Only anonymized numbers sent ✅
- No message content ever ✅
- No PII collected ✅
- Zero retention policy ✅

**We NEVER:**
- Collect message content ❌
- Store personal data ❌
- Sell your data ❌
- Track your browsing ❌

**Our Promise:**
Privacy is not optional. It's fundamental to UniversalShield.

---

**UniversalShield Team**  
*Protecting you from scams, protecting your privacy always.*
