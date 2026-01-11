"""
Database Service - PostgreSQL Integration
Handles persistent storage for feedback, licenses, and ML training data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Dict, List, Optional
from datetime import datetime, date
import json


class DatabaseService:
    """PostgreSQL database service for UniversalShield."""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database."""
        try:
            # Get connection details from environment or use defaults
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'universalshield'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres')
            )
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("   Using in-memory fallback (data will not persist)")
            self.conn = None
    
    def execute_schema(self, schema_path: str):
        """Execute SQL schema file to create tables."""
        if not self.conn:
            return False
        
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            with self.conn.cursor() as cursor:
                cursor.execute(schema_sql)
                self.conn.commit()
            
            print(f"✅ Database schema initialized from {schema_path}")
            return True
        except Exception as e:
            print(f"❌ Schema execution failed: {e}")
            return False
    
    # License Management
    
    def validate_license(self, license_key: str) -> Optional[Dict]:
        """Validate license key and return license info."""
        if not self.conn:
            return None
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    UPDATE licenses 
                    SET last_validated = CURRENT_TIMESTAMP
                    WHERE license_key = %s AND active = TRUE
                    RETURNING license_key, email, tier, active, scans_used_today, scans_reset_date
                """, (license_key,))
                
                result = cursor.fetchone()
                self.conn.commit()
                
                if result:
                    # Reset daily scan count if new day
                    if result['scans_reset_date'] != date.today():
                        cursor.execute("""
                            UPDATE licenses 
                            SET scans_used_today = 0, scans_reset_date = CURRENT_DATE
                            WHERE license_key = %s
                        """, (license_key,))
                        self.conn.commit()
                        result['scans_used_today'] = 0
                
                return dict(result) if result else None
        except Exception as e:
            print(f"❌ License validation error: {e}")
            return None
    
    def increment_scan_count(self, license_key: str):
        """Increment daily scan count for a license."""
        if not self.conn:
            return
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE licenses 
                    SET scans_used_today = scans_used_today + 1
                    WHERE license_key = %s
                """, (license_key,))
                self.conn.commit()
        except Exception as e:
            print(f"❌ Scan count increment error: {e}")
    
    def create_license(self, email: str, tier: str = 'free', subscription_id: Optional[str] = None) -> str:
        """Create a new license key."""
        if not self.conn:
            return None
        
        import secrets
        license_key = f"US-{'PRO' if tier == 'pro' else 'FREE'}-{secrets.token_hex(8).upper()}"
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO licenses (license_key, email, tier, subscription_id)
                    VALUES (%s, %s, %s, %s)
                """, (license_key, email, tier, subscription_id))
                self.conn.commit()
            
            print(f"✅ Created license: {license_key} ({tier})")
            return license_key
        except Exception as e:
            print(f"❌ License creation error: {e}")
            return None
    
    def deactivate_license(self, license_key: str):
        """Deactivate a license (subscription cancelled)."""
        if not self.conn:
            return
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE licenses 
                    SET active = FALSE
                    WHERE license_key = %s
                """, (license_key,))
                self.conn.commit()
            
            print(f"✅ Deactivated license: {license_key}")
        except Exception as e:
            print(f"❌ License deactivation error: {e}")
    
    # Scam Reports (ML Training Data)
    
    def save_scam_report(self, features: Dict, predicted_risk_score: float, 
                        predicted_risk_level: str, is_scam: bool, 
                        license_key: Optional[str] = None, platform: str = 'linkedin'):
        """Save user feedback (scam report or false positive)."""
        if not self.conn:
            return None
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO scam_reports 
                    (license_key, features, predicted_risk_score, predicted_risk_level, 
                     is_scam, platform)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (license_key, Json(features), predicted_risk_score, 
                      predicted_risk_level, is_scam, platform))
                
                report_id = cursor.fetchone()[0]
                self.conn.commit()
            
            print(f"✅ Saved scam report #{report_id} (is_scam={is_scam})")
            return report_id
        except Exception as e:
            print(f"❌ Scam report save error: {e}")
            return None
    
    def get_training_data(self, limit: int = 1000, unused_only: bool = True) -> List[Dict]:
        """Get labeled data for ML training."""
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT id, features, is_scam, platform, reported_at
                    FROM scam_reports
                """
                if unused_only:
                    query += " WHERE used_for_training = FALSE"
                query += f" ORDER BY reported_at DESC LIMIT {limit}"
                
                cursor.execute(query)
                results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Training data fetch error: {e}")
            return []
    
    def mark_reports_as_used(self, report_ids: List[int], batch_id: int):
        """Mark reports as used for training."""
        if not self.conn or not report_ids:
            return
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE scam_reports 
                    SET used_for_training = TRUE, training_batch_id = %s
                    WHERE id = ANY(%s)
                """, (batch_id, report_ids))
                self.conn.commit()
            
            print(f"✅ Marked {len(report_ids)} reports as used for training")
        except Exception as e:
            print(f"❌ Mark reports error: {e}")
    
    # API Request Logging
    
    def log_api_request(self, license_key: Optional[str], endpoint: str, 
                       response_time_ms: int, risk_score: Optional[int] = None,
                       risk_level: Optional[str] = None, tier: str = 'free'):
        """Log API request for analytics."""
        if not self.conn:
            return
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_requests 
                    (license_key, endpoint, response_time_ms, risk_score, risk_level, tier)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (license_key, endpoint, response_time_ms, risk_score, risk_level, tier))
                self.conn.commit()
        except Exception as e:
            print(f"❌ API request log error: {e}")
    
    # ML Model Management
    
    def save_model_version(self, version: str, model_type: str, 
                          training_samples: int, metrics: Dict,
                          model_path: str, feature_count: int) -> Optional[int]:
        """Save ML model version and metrics."""
        if not self.conn:
            return None
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO model_versions 
                    (version, model_type, training_samples_count, accuracy, 
                     precision_score, recall, f1_score, model_path, feature_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (version, model_type, training_samples, 
                      metrics.get('accuracy'), metrics.get('precision'),
                      metrics.get('recall'), metrics.get('f1_score'),
                      model_path, feature_count))
                
                model_id = cursor.fetchone()[0]
                self.conn.commit()
            
            print(f"✅ Saved model version: {version} (ID: {model_id})")
            return model_id
        except Exception as e:
            print(f"❌ Model version save error: {e}")
            return None
    
    def set_active_model(self, model_id: int):
        """Set a model version as active (deployed)."""
        if not self.conn:
            return
        
        try:
            with self.conn.cursor() as cursor:
                # Deactivate all models
                cursor.execute("UPDATE model_versions SET is_active = FALSE")
                
                # Activate selected model
                cursor.execute("""
                    UPDATE model_versions 
                    SET is_active = TRUE, deployed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (model_id,))
                
                self.conn.commit()
            
            print(f"✅ Activated model ID: {model_id}")
        except Exception as e:
            print(f"❌ Model activation error: {e}")
    
    # Analytics
    
    def update_daily_metrics(self, metric_date: date = None):
        """Update daily metrics from logs."""
        if not self.conn:
            return
        
        if not metric_date:
            metric_date = date.today()
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO daily_metrics (
                        metric_date, total_scans, scams_detected, 
                        free_tier_scans, pro_tier_scans, avg_response_time_ms
                    )
                    SELECT 
                        DATE(%s),
                        COUNT(*),
                        SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN tier = 'free' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN tier = 'pro' THEN 1 ELSE 0 END),
                        AVG(response_time_ms)::INTEGER
                    FROM api_requests
                    WHERE DATE(request_timestamp) = DATE(%s)
                    ON CONFLICT (metric_date) DO UPDATE SET
                        total_scans = EXCLUDED.total_scans,
                        scams_detected = EXCLUDED.scams_detected,
                        free_tier_scans = EXCLUDED.free_tier_scans,
                        pro_tier_scans = EXCLUDED.pro_tier_scans,
                        avg_response_time_ms = EXCLUDED.avg_response_time_ms
                """, (metric_date, metric_date))
                
                self.conn.commit()
        except Exception as e:
            print(f"❌ Metrics update error: {e}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
