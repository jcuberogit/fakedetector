# UniversalShield Setup Guide

Complete setup instructions for deploying the UniversalShield VPS Agent and Chrome Extension.

---

## 📋 Prerequisites

- **Python 3.9+**
- **PostgreSQL 14+**
- **Node.js 16+** (for extension development)
- **VPS Server** (Hetzner, DigitalOcean, AWS, etc.)
- **Domain** with SSL (Let's Encrypt)

---

## 🗄️ Database Setup

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@14
brew services start postgresql@14
```

### 2. Create Database

```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE universalshield;
CREATE USER universalshield_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE universalshield TO universalshield_user;
\q
```

### 3. Initialize Schema

```bash
cd /Users/jcubero/ParadigmStore/agents/paradigm.fraud.agent

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=universalshield
export DB_USER=universalshield_user
export DB_PASSWORD=your_secure_password

# Run schema initialization
psql -U universalshield_user -d universalshield -f src/db/schema.sql
```

---

## 🐍 Python Environment Setup

### 1. Create Virtual Environment

```bash
cd /Users/jcubero/ParadigmStore/agents/paradigm.fraud.agent

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import fastapi, xgboost, psycopg2; print('✅ All dependencies installed')"
```

---

## 🤖 Train Initial ML Model

### 1. Create Training Data (Optional)

If you don't have user feedback yet, create initial training data:

```bash
mkdir -p data
# Create data/scam_examples.json with labeled examples
```

### 2. Train Model

```bash
python src/ml/train_model.py
```

Expected output:
```
✅ TARGET MET: Model ready for production!
   Precision: 87.5% (target: ≥85%)
   Recall: 82.3% (target: ≥80%)
```

The trained model will be saved to `models/scam_detector_v1.pkl`.

---

## 🚀 Start VPS Agent API

### 1. Local Development

```bash
# Start API server
uvicorn src.api.scam_detection_api:app --reload --port 8000

# Test endpoint
curl http://localhost:8000/
```

### 2. Production Deployment

Create `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=universalshield
DB_USER=universalshield_user
DB_PASSWORD=your_secure_password

# API
API_HOST=0.0.0.0
API_PORT=8000
```

Start with systemd:

```bash
sudo nano /etc/systemd/system/universalshield.service
```

```ini
[Unit]
Description=UniversalShield Fraud Detection API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/universalshield
Environment="PATH=/var/www/universalshield/venv/bin"
EnvironmentFile=/var/www/universalshield/.env
ExecStart=/var/www/universalshield/venv/bin/uvicorn src.api.scam_detection_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable universalshield
sudo systemctl start universalshield
sudo systemctl status universalshield
```

### 3. Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/universalshield
```

```nginx
server {
    listen 80;
    server_name api.tucan.store;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/universalshield /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.tucan.store
```

---

## 🔄 Weekly Model Retraining

### 1. Start Scheduler

```bash
# Development
python src/ml/retrain_scheduler.py

# Production (systemd)
sudo nano /etc/systemd/system/universalshield-retrain.service
```

```ini
[Unit]
Description=UniversalShield Model Retraining Scheduler
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/universalshield
Environment="PATH=/var/www/universalshield/venv/bin"
EnvironmentFile=/var/www/universalshield/.env
ExecStart=/var/www/universalshield/venv/bin/python src/ml/retrain_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable universalshield-retrain
sudo systemctl start universalshield-retrain
```

---

## 🧩 Chrome Extension Setup

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `/Users/jcubero/ParadigmStore/agents/paradigm.fraud.agent/extensions`

### 2. Configure API Endpoint

The extension is pre-configured to use `https://api.tucan.store`.

To change the endpoint, edit `extensions/src/cloudAnalyzer.js`:

```javascript
this.apiUrl = apiUrl || 'https://your-api-domain.com';
```

### 3. Test Extension

1. Go to LinkedIn messages
2. Open a message
3. Extension should automatically scan and show badges for suspicious content

---

## 🔑 License Management

### 1. Create Demo License

Demo license `US-PRO-DEMO12345678` is automatically created in the database.

### 2. Create New License

```python
from src.db.database import DatabaseService

db = DatabaseService()
license_key = db.create_license(
    email="user@example.com",
    tier="pro",
    subscription_id="PAYPAL_SUB_123"
)
print(f"License created: {license_key}")
db.close()
```

### 3. Activate License in Extension

1. Open extension popup
2. Right-click "Upgrade" button
3. Enter license key
4. Click "Activate"

---

## 📊 Monitoring & Analytics

### 1. Check API Health

```bash
curl https://api.tucan.store/
```

### 2. View Database Metrics

```sql
-- Daily metrics
SELECT * FROM daily_metrics ORDER BY metric_date DESC LIMIT 7;

-- Active licenses
SELECT COUNT(*) FROM licenses WHERE active = TRUE;

-- Training data available
SELECT COUNT(*) FROM scam_reports WHERE used_for_training = FALSE;
```

### 3. Model Performance

```sql
SELECT version, accuracy, precision_score, recall, f1_score, is_active
FROM model_versions
ORDER BY trained_at DESC
LIMIT 5;
```

---

## 🧪 Testing

### 1. Test VPS API

```bash
# Test analyze-features endpoint
curl -X POST https://api.tucan.store/api/v1/analyze-features \
  -H "Content-Type: application/json" \
  -H "X-License-Key: US-PRO-DEMO12345678" \
  -d '{
    "features": {
      "message_length": 150,
      "urgency_keywords_count": 3,
      "money_keywords_count": 2,
      "gmail_recruiter_combo": 1
    }
  }'
```

Expected response:
```json
{
  "risk_score": 75,
  "risk_level": "caution",
  "explanation": "High urgency + financial keywords detected",
  "ml_confidence": 0.92,
  "tier": "pro"
}
```

### 2. Test License Validation

```bash
curl -X POST https://api.tucan.store/api/v1/subscription/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "US-PRO-DEMO12345678"}'
```

---

## 🔧 Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U universalshield_user -d universalshield -c "SELECT 1;"
```

### API Not Responding

```bash
# Check service status
sudo systemctl status universalshield

# View logs
sudo journalctl -u universalshield -f
```

### Extension Not Working

1. Check browser console (F12) for errors
2. Verify API endpoint is accessible
3. Check license key is valid
4. Reload extension

### Model Training Fails

```bash
# Check training data exists
python -c "from src.db.database import DatabaseService; db = DatabaseService(); print(len(db.get_training_data())); db.close()"

# If no data, create initial dataset or wait for user reports
```

---

## 📚 Next Steps

1. **Deploy to VPS**: Follow production deployment steps
2. **Configure DNS**: Point `api.tucan.store` to your VPS IP
3. **Set up SSL**: Use Let's Encrypt for HTTPS
4. **Add Payment Flow**: Integrate Stripe/PayPal (see `UNIVERSALSHIELD_TICKET.md` Phase 7)
5. **Submit to Chrome Web Store**: Package extension for distribution
6. **Monitor Performance**: Set up logging and alerting

---

## 🆘 Support

- **Documentation**: `UNIVERSALSHIELD_TICKET.md`
- **Architecture**: `ARCHITECTURE.md`
- **Tickets**: `UniversalShield-Tickets.csv`
- **Realignment Summary**: `REALIGNMENT_SUMMARY.md`

---

**Created:** January 10, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
