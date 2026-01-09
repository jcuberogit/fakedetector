# UniversalShield VPS Deployment Checklist

Step-by-step checklist for deploying UniversalShield to Hetzner VPS.

---

## 🎯 Overview

**Total Time:** ~1 hour  
**Cost:** $5.83/month  
**Difficulty:** Easy (copy-paste commands)

---

## ✅ Pre-Deployment Checklist

### Before You Start:

- [ ] GitHub account with universalshield repo
- [ ] Credit card or PayPal for VPS payment
- [ ] Domain name (optional but recommended)
  - Suggested: `api.universalshield.dev`
  - Or use IP address for testing
- [ ] SSH key generated on your Mac
  - Check: `ls ~/.ssh/id_rsa.pub`
  - If not: `ssh-keygen -t rsa -b 4096`

---

## 📋 Step-by-Step Deployment

### **PHASE 1: VPS Setup (10 minutes)**

#### Step 1.1: Create Hetzner Account
- [ ] Go to https://console.hetzner.cloud/
- [ ] Sign up with email
- [ ] Verify email address
- [ ] Add payment method (credit card or PayPal)

#### Step 1.2: Create Project
- [ ] Click "New Project"
- [ ] Name: `UniversalShield`
- [ ] Click "Create"

#### Step 1.3: Add SSH Key
- [ ] In Hetzner dashboard, go to "Security" → "SSH Keys"
- [ ] Click "Add SSH Key"
- [ ] Paste your public key:
  ```bash
  cat ~/.ssh/id_rsa.pub
  ```
- [ ] Name: `mac-laptop`
- [ ] Click "Add SSH Key"

#### Step 1.4: Create Server
- [ ] Click "Add Server"
- [ ] **Location:** Ashburn, VA (us-east) ← Best for US/global
- [ ] **Image:** Ubuntu 22.04
- [ ] **Type:** Shared vCPU → **CPX11** (2 vCPU, 2GB RAM)
- [ ] **Volume:** None
- [ ] **Networking:** Default
- [ ] **SSH Keys:** Select your key
- [ ] **Name:** `universalshield-api`
- [ ] Click "Create & Buy"

#### Step 1.5: Wait for Server
- [ ] Wait ~60 seconds for provisioning
- [ ] Note the IP address (e.g., `123.45.67.89`)
- [ ] Copy IP to clipboard

---

### **PHASE 2: Initial Server Configuration (10 minutes)**

#### Step 2.1: Connect to Server
```bash
# Replace with your server IP
ssh root@YOUR_SERVER_IP
```

Expected: You're now logged into the VPS!

#### Step 2.2: Update System
```bash
apt update && apt upgrade -y
```

Wait ~2 minutes for updates.

#### Step 2.3: Install Required Packages
```bash
apt install -y python3.11 python3-pip python3-venv git \
  nginx certbot python3-certbot-nginx \
  postgresql postgresql-contrib ufw
```

Wait ~3 minutes for installation.

#### Step 2.4: Verify Python Version
```bash
python3 --version
```

Expected output: `Python 3.11.x` ✅

#### Step 2.5: Create Application User
```bash
adduser universalshield
# Set password when prompted
# Press Enter for all other prompts (use defaults)

# Add to sudo group
usermod -aG sudo universalshield

# Switch to new user
su - universalshield
```

You're now logged in as `universalshield` user.

---

### **PHASE 3: Deploy Application (15 minutes)**

#### Step 3.1: Clone Repository
```bash
cd ~
git clone https://github.com/jcuberogit/universalshield.git
cd universalshield
```

#### Step 3.2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)`.

#### Step 3.3: Upgrade pip
```bash
pip install --upgrade pip
```

#### Step 3.4: Install Dependencies
```bash
pip install -r requirements.txt
```

**This is the critical step!** With Python 3.11, all packages should install smoothly.

Expected: No errors, all packages installed ✅

If you see errors, STOP and report them.

#### Step 3.5: Verify Installation
```bash
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import xgboost; print('XGBoost:', xgboost.__version__)"
```

Expected output:
```
FastAPI: 0.104.1
XGBoost: 2.0.2
```

---

### **PHASE 4: Test Application (10 minutes)**

#### Step 4.1: Run Integration Tests
```bash
python tests/test_integration.py
```

Expected output:
```
============================================================
INTEGRATION TEST SUMMARY
============================================================
Passed: 33
Failed: 0
Warnings: 0

✅ ALL TESTS PASSED - READY FOR DEPLOYMENT
```

If any tests fail, STOP and investigate.

#### Step 4.2: Train ML Model
```bash
python src/ml/train_model.py
```

Expected output:
```
✅ TARGET MET: Model ready for production!
   Precision: 87.5% (target: ≥85%)
   Recall: 83.3% (target: ≥80%)
```

Model saved to: `models/scam_detector_v1.pkl`

#### Step 4.3: Test API Server
```bash
# Start server in background
uvicorn src.api.scam_detection_api:app --host 0.0.0.0 --port 8000 &

# Wait 2 seconds
sleep 2

# Test health endpoint
curl http://localhost:8000/

# Expected output:
# {
#   "service": "UniversalShield API",
#   "version": "1.0.0",
#   "status": "operational"
# }

# Stop server
pkill -f uvicorn
```

---

### **PHASE 5: Configure Environment (5 minutes)**

#### Step 5.1: Create .env File
```bash
nano .env
```

Paste this configuration:
```bash
# API Configuration
API_URL=https://api.universalshield.dev
ENVIRONMENT=production

# PayPal Configuration (use sandbox for now)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_SECRET=your_sandbox_secret
PAYPAL_MONTHLY_PLAN_ID=P-XXXXXXXXXXXX
PAYPAL_ANNUAL_PLAN_ID=P-XXXXXXXXXXXX

# Database Configuration
DATABASE_URL=postgresql://universalshield:your_password@localhost/universalshield

# Security (generate random keys)
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Logging
LOG_LEVEL=WARNING
DATA_RETENTION=0
```

Save: `Ctrl+X`, `Y`, `Enter`

#### Step 5.2: Setup Database
```bash
# Exit to root user
exit

# Create database
sudo -u postgres psql -c "CREATE DATABASE universalshield;"
sudo -u postgres psql -c "CREATE USER universalshield WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE universalshield TO universalshield;"

# Back to universalshield user
su - universalshield
cd universalshield
```

---

### **PHASE 6: Setup Systemd Service (5 minutes)**

#### Step 6.1: Create Service File
```bash
# Exit to root
exit

# Create service file
sudo nano /etc/systemd/system/universalshield.service
```

Paste this:
```ini
[Unit]
Description=UniversalShield API
After=network.target

[Service]
Type=simple
User=universalshield
WorkingDirectory=/home/universalshield/universalshield
Environment="PATH=/home/universalshield/universalshield/venv/bin"
EnvironmentFile=/home/universalshield/universalshield/.env
ExecStart=/home/universalshield/universalshield/venv/bin/uvicorn src.api.scam_detection_api:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

#### Step 6.2: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable universalshield
sudo systemctl start universalshield
sudo systemctl status universalshield
```

Expected: `active (running)` in green ✅

#### Step 6.3: Test API
```bash
curl http://localhost:8000/
```

Expected: JSON response with service info ✅

---

### **PHASE 7: Configure Nginx (5 minutes)**

#### Step 7.1: Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/universalshield
```

Paste this:
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;  # Replace with your IP or domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Replace `YOUR_SERVER_IP` with your actual IP.

Save: `Ctrl+X`, `Y`, `Enter`

#### Step 7.2: Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/universalshield /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Expected: `nginx: configuration file test is successful` ✅

#### Step 7.3: Configure Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
# Type 'y' when prompted
sudo ufw status
```

Expected: Firewall active with SSH and Nginx allowed ✅

---

### **PHASE 8: Test Public Access (2 minutes)**

#### Step 8.1: Test from Your Mac
```bash
# On your Mac (not VPS)
curl http://YOUR_SERVER_IP/
```

Expected: JSON response from API ✅

#### Step 8.2: Test in Browser
Open browser and go to:
```
http://YOUR_SERVER_IP/
```

You should see the API response!

---

## 🎉 **DEPLOYMENT COMPLETE!**

Your UniversalShield API is now live at:
```
http://YOUR_SERVER_IP/
```

---

## 🔍 **Verification Checklist**

Run these commands to verify everything works:

```bash
# On VPS:
sudo systemctl status universalshield  # Should be active
curl http://localhost:8000/            # Should return JSON
sudo journalctl -u universalshield -n 20  # Check logs

# On your Mac:
curl http://YOUR_SERVER_IP/            # Should return JSON
```

All green? **You're ready for production!** ✅

---

## 📊 **What You've Deployed**

- ✅ FastAPI server running on port 8000
- ✅ Nginx reverse proxy on port 80
- ✅ Systemd service (auto-restart on failure)
- ✅ Firewall configured (UFW)
- ✅ PostgreSQL database ready
- ✅ ML model trained and loaded
- ✅ All 33 integration tests passing

---

## 🚀 **Next Steps**

### Immediate:
1. **Test API endpoints:**
   ```bash
   curl -X POST http://YOUR_SERVER_IP/api/v1/analyze-features \
     -H "Content-Type: application/json" \
     -d '{"features": {"message_length": 100}}'
   ```

2. **Update extension:**
   - Edit `extensions/UniversalShield/src/cloudAnalyzer.js`
   - Change API URL to `http://YOUR_SERVER_IP`
   - Load extension in Chrome
   - Test on LinkedIn

### This Week:
3. **Setup domain & SSL:**
   - Point domain to server IP
   - Run: `sudo certbot --nginx -d api.universalshield.dev`
   - Update extension to use HTTPS

4. **Configure PayPal:**
   - Follow `docs/PAYPAL_SETUP_GUIDE.md`
   - Update `.env` with live credentials

### Next Week:
5. **Submit to Chrome Web Store:**
   - Follow `docs/CHROME_WEB_STORE_GUIDE.md`
   - Create assets (icons, screenshots)
   - Submit for review

---

## 🐛 **Troubleshooting**

### API not responding:
```bash
sudo systemctl status universalshield
sudo journalctl -u universalshield -n 50
```

### Nginx errors:
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Database issues:
```bash
sudo -u postgres psql
\l  # List databases
\du # List users
```

### Restart everything:
```bash
sudo systemctl restart universalshield
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

---

## 💰 **Monthly Costs**

- Hetzner VPS: $5.83/month
- Domain (.dev): $1/month (optional)
- **Total: ~$7/month**

With 1,000 users and 5% conversion to Pro ($4.99/month):
- Revenue: $250/month
- Costs: $7/month
- **Profit: $243/month** 🎉

---

## 📞 **Support**

If you get stuck:
1. Check logs: `sudo journalctl -u universalshield -n 100`
2. Review deployment guide: `docs/DEPLOYMENT_GUIDE.md`
3. GitHub issues: https://github.com/jcuberogit/universalshield/issues

---

**Ready to deploy?** Follow this checklist step-by-step and you'll have UniversalShield live in ~1 hour! 🛡️
