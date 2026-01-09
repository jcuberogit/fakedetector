# UniversalShield Deployment Guide

Complete guide to deploying UniversalShield to production (Hetzner VPS).

---

## Prerequisites

- Hetzner Cloud account
- Domain name (api.universalshield.dev)
- PayPal Business account
- GitHub account

---

## Step 1: VPS Setup (Hetzner)

### 1.1 Create Server

1. Go to https://console.hetzner.cloud/
2. Create new project: "UniversalShield"
3. Add server:
   - **Location:** Nuremberg, Germany (or closest to target users)
   - **Image:** Ubuntu 22.04
   - **Type:** CPX11 (2 vCPU, 2GB RAM) - $5.83/month
   - **Volume:** None needed initially
   - **SSH Key:** Add your public key

4. Click **Create & Buy**
5. Note the server IP address

### 1.2 Initial Server Configuration

SSH into server:
```bash
ssh root@YOUR_SERVER_IP
```

Update system:
```bash
apt update && apt upgrade -y
```

Install required packages:
```bash
apt install -y python3.11 python3-pip python3-venv nginx certbot python3-certbot-nginx git postgresql postgresql-contrib
```

Create application user:
```bash
adduser universalshield
usermod -aG sudo universalshield
su - universalshield
```

---

## Step 2: Domain Configuration

### 2.1 DNS Setup

In your domain registrar (Namecheap, GoDaddy, etc.):

1. Add A record:
   - **Host:** api
   - **Value:** YOUR_SERVER_IP
   - **TTL:** 300

2. Wait for DNS propagation (5-30 minutes)
3. Verify: `dig api.universalshield.dev`

---

## Step 3: Application Deployment

### 3.1 Clone Repository

```bash
cd /home/universalshield
git clone https://github.com/jcuberogit/universalshield.git
cd universalshield
```

### 3.2 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Configure Environment Variables

Create `.env` file:
```bash
nano .env
```

Add configuration:
```bash
# API Configuration
API_URL=https://api.universalshield.dev
ENVIRONMENT=production

# PayPal Configuration
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=your_live_client_id_here
PAYPAL_SECRET=your_live_secret_here
PAYPAL_MONTHLY_PLAN_ID=P-XXXXXXXXXXXX
PAYPAL_ANNUAL_PLAN_ID=P-XXXXXXXXXXXX

# Database Configuration
DATABASE_URL=postgresql://universalshield:your_password@localhost/universalshield

# Security
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Logging
LOG_LEVEL=WARNING
DATA_RETENTION=0
```

Save and exit (Ctrl+X, Y, Enter)

### 3.4 Setup Database

```bash
sudo -u postgres psql
```

In PostgreSQL:
```sql
CREATE DATABASE universalshield;
CREATE USER universalshield WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE universalshield TO universalshield;
\q
```

Run migrations (if using Alembic):
```bash
alembic upgrade head
```

### 3.5 Train ML Model

```bash
python src/ml/train_model.py
```

Expected output:
```
✅ TARGET MET: Model ready for production!
   Precision: 87.5% (target: ≥85%)
   Recall: 83.3% (target: ≥80%)
```

---

## Step 4: Systemd Service

### 4.1 Create Service File

```bash
sudo nano /etc/systemd/system/universalshield.service
```

Add configuration:
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

### 4.2 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable universalshield
sudo systemctl start universalshield
sudo systemctl status universalshield
```

Verify it's running:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "service": "UniversalShield API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

## Step 5: Nginx Configuration

### 5.1 Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/universalshield
```

Add configuration:
```nginx
server {
    listen 80;
    server_name api.universalshield.dev;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.universalshield.dev;

    # SSL certificates (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/api.universalshield.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.universalshield.dev/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Privacy: No request body logging
    access_log /var/log/nginx/universalshield_access.log combined;
    error_log /var/log/nginx/universalshield_error.log;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

### 5.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/universalshield /etc/nginx/sites-enabled/
sudo nginx -t
```

---

## Step 6: SSL Certificate (Let's Encrypt)

### 6.1 Obtain Certificate

```bash
sudo certbot --nginx -d api.universalshield.dev
```

Follow prompts:
- Email: your@email.com
- Agree to terms: Yes
- Redirect HTTP to HTTPS: Yes

### 6.2 Auto-Renewal

Certbot auto-renewal is enabled by default. Test it:
```bash
sudo certbot renew --dry-run
```

---

## Step 7: Firewall Configuration

### 7.1 Setup UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

---

## Step 8: Monitoring & Logging

### 8.1 Check Service Logs

```bash
# API logs
sudo journalctl -u universalshield -f

# Nginx logs
sudo tail -f /var/log/nginx/universalshield_access.log
sudo tail -f /var/log/nginx/universalshield_error.log
```

### 8.2 Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/universalshield
```

Add:
```
/var/log/nginx/universalshield_*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## Step 9: Testing

### 9.1 API Health Check

```bash
curl https://api.universalshield.dev/
```

Expected:
```json
{
  "service": "UniversalShield API",
  "version": "1.0.0",
  "status": "operational",
  "privacy": "Zero-retention policy - no data stored"
}
```

### 9.2 Test Analysis Endpoint

```bash
curl -X POST https://api.universalshield.dev/api/v1/analyze-features \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "message_length": 450,
      "urgency_keywords_count": 3,
      "file_extension_risk": 0.95,
      "sender_account_age_days": 2
    }
  }'
```

### 9.3 Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 https://api.universalshield.dev/
```

---

## Step 10: Backup Strategy

### 10.1 Database Backup

Create backup script:
```bash
nano /home/universalshield/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/universalshield/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump universalshield > $BACKUP_DIR/db_$DATE.sql

# Backup .env
cp /home/universalshield/universalshield/.env $BACKUP_DIR/env_$DATE.bak

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable:
```bash
chmod +x /home/universalshield/backup.sh
```

### 10.2 Schedule Backups

```bash
crontab -e
```

Add:
```
0 2 * * * /home/universalshield/backup.sh >> /home/universalshield/backup.log 2>&1
```

---

## Step 11: Update Procedure

When you need to deploy updates:

```bash
cd /home/universalshield/universalshield
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart universalshield
sudo systemctl status universalshield
```

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Hetzner VPS (CPX11) | $5.83/mo | 2 vCPU, 2GB RAM |
| Domain (.dev) | $12/year | One-time + renewal |
| SSL Certificate | FREE | Let's Encrypt |
| **Total** | **~$6/mo** | Very affordable! |

---

## Performance Optimization

### Enable Gzip Compression

Add to Nginx config:
```nginx
gzip on;
gzip_vary on;
gzip_types text/plain application/json;
```

### Database Connection Pooling

In your API, use SQLAlchemy connection pooling:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

---

## Security Checklist

- [x] Firewall enabled (UFW)
- [x] SSH key authentication only
- [x] SSL/TLS enabled (Let's Encrypt)
- [x] Security headers configured
- [x] Rate limiting enabled
- [x] No request body logging (privacy)
- [x] Environment variables secured
- [x] Database password strong
- [x] Regular backups scheduled
- [x] Auto-updates enabled

---

## Troubleshooting

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

### Database connection issues:
```bash
sudo -u postgres psql
\l  # List databases
\du # List users
```

### SSL certificate issues:
```bash
sudo certbot certificates
sudo certbot renew --force-renewal
```

---

## Monitoring Dashboard (Optional)

Install Grafana + Prometheus for monitoring:
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*
./prometheus --config.file=prometheus.yml

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana
sudo systemctl start grafana-server
```

Access Grafana at: `http://YOUR_SERVER_IP:3000`

---

## Success Criteria

✅ API responds at https://api.universalshield.dev/  
✅ SSL certificate valid  
✅ Service auto-starts on reboot  
✅ Logs are being written  
✅ Backups running daily  
✅ Rate limiting working  
✅ PayPal webhook receiving events  

---

## Next Steps After Deployment

1. Update Chrome extension with production API URL
2. Submit extension to Chrome Web Store
3. Set up monitoring alerts
4. Create status page (status.universalshield.dev)
5. Launch marketing campaign

---

**Your UniversalShield API is now live! 🚀**

Monitor it closely for the first few days and be ready to scale if needed.
