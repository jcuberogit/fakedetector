"""
Admin API - Dashboard endpoints for monitoring and analytics
Requires authentication token for access
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os

from src.db.database import DatabaseService
from src.ml.fraud_ring_detector import FraudRingDetector

router = APIRouter(prefix="/api/v1/admin")

# Admin authentication
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin_secret_token_change_me')

def verify_admin_token(authorization: Optional[str] = Header(None)):
    """Verify admin authentication token."""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace('Bearer ', '')
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    return True

# Initialize services
db = DatabaseService()
fraud_detector = FraudRingDetector(db)


@router.get("/metrics")
async def get_metrics(authorized: bool = Depends(verify_admin_token)):
    """Get key dashboard metrics."""
    try:
        cursor = db.conn.cursor()
        
        # Today's metrics
        cursor.execute("""
            SELECT total_scans, scams_detected, free_tier_scans, pro_tier_scans
            FROM daily_metrics
            WHERE metric_date = CURRENT_DATE
        """)
        today = cursor.fetchone()
        
        # Active licenses count
        cursor.execute("""
            SELECT COUNT(*) FROM licenses WHERE active = TRUE AND tier = 'pro'
        """)
        active_licenses = cursor.fetchone()[0]
        
        # Active fraud rings
        cursor.execute("""
            SELECT COUNT(*) FROM fraud_rings WHERE status = 'active'
        """)
        fraud_rings = cursor.fetchone()[0]
        
        cursor.close()
        
        return {
            "total_scans": today[0] if today else 0,
            "scams_detected": today[1] if today else 0,
            "free_tier_scans": today[2] if today else 0,
            "pro_tier_scans": today[3] if today else 0,
            "active_licenses": active_licenses,
            "fraud_rings": fraud_rings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@router.get("/recent-requests")
async def get_recent_requests(
    limit: int = 50,
    authorized: bool = Depends(verify_admin_token)
):
    """Get recent API requests."""
    try:
        cursor = db.conn.cursor()
        
        cursor.execute("""
            SELECT 
                request_timestamp as timestamp,
                endpoint,
                tier,
                risk_level,
                response_time_ms
            FROM api_requests
            ORDER BY request_timestamp DESC
            LIMIT %s
        """, (limit,))
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                "timestamp": row[0].isoformat(),
                "endpoint": row[1],
                "tier": row[2],
                "risk_level": row[3],
                "response_time_ms": row[4]
            })
        
        cursor.close()
        return requests
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Requests error: {str(e)}")


@router.get("/licenses")
async def get_licenses(
    active_only: bool = True,
    authorized: bool = Depends(verify_admin_token)
):
    """Get all licenses."""
    try:
        cursor = db.conn.cursor()
        
        query = """
            SELECT 
                license_key, email, tier, active, 
                scans_used_today, created_at
            FROM licenses
        """
        
        if active_only:
            query += " WHERE active = TRUE"
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        
        licenses = []
        for row in cursor.fetchall():
            licenses.append({
                "license_key": row[0],
                "email": row[1],
                "tier": row[2],
                "active": row[3],
                "scans_used_today": row[4],
                "created_at": row[5].isoformat()
            })
        
        cursor.close()
        return licenses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Licenses error: {str(e)}")


@router.get("/fraud-rings")
async def get_fraud_rings(
    active_only: bool = True,
    authorized: bool = Depends(verify_admin_token)
):
    """Get detected fraud rings."""
    try:
        cursor = db.conn.cursor()
        
        query = """
            SELECT 
                ring_identifier, detected_at, member_count,
                confidence_score, pattern_type, status
            FROM fraud_rings
        """
        
        if active_only:
            query += " WHERE status = 'active'"
        
        query += " ORDER BY detected_at DESC"
        
        cursor.execute(query)
        
        rings = []
        for row in cursor.fetchall():
            rings.append({
                "ring_identifier": row[0],
                "detected_at": row[1].isoformat(),
                "member_count": row[2],
                "confidence_score": float(row[3]) if row[3] else 0.0,
                "pattern_type": row[4],
                "status": row[5]
            })
        
        cursor.close()
        return rings
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud rings error: {str(e)}")


@router.get("/models")
async def get_models(
    limit: int = 10,
    authorized: bool = Depends(verify_admin_token)
):
    """Get ML model versions and performance."""
    try:
        cursor = db.conn.cursor()
        
        cursor.execute("""
            SELECT 
                version, model_type, accuracy, precision_score,
                recall, f1_score, trained_at, is_active
            FROM model_versions
            ORDER BY trained_at DESC
            LIMIT %s
        """, (limit,))
        
        models = []
        for row in cursor.fetchall():
            models.append({
                "version": row[0],
                "model_type": row[1],
                "accuracy": float(row[2]) if row[2] else 0.0,
                "precision_score": float(row[3]) if row[3] else 0.0,
                "recall": float(row[4]) if row[4] else 0.0,
                "f1_score": float(row[5]) if row[5] else 0.0,
                "trained_at": row[6].isoformat(),
                "is_active": row[7]
            })
        
        cursor.close()
        return models
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Models error: {str(e)}")


@router.get("/training-data")
async def get_training_data(
    authorized: bool = Depends(verify_admin_token)
):
    """Get training data statistics."""
    try:
        cursor = db.conn.cursor()
        
        # Total reports
        cursor.execute("SELECT COUNT(*) FROM scam_reports")
        total_reports = cursor.fetchone()[0]
        
        # Unused reports
        cursor.execute("SELECT COUNT(*) FROM scam_reports WHERE used_for_training = FALSE")
        unused_reports = cursor.fetchone()[0]
        
        # Scam vs legitimate distribution
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN is_scam THEN 1 ELSE 0 END) as scams,
                SUM(CASE WHEN NOT is_scam THEN 1 ELSE 0 END) as legitimate
            FROM scam_reports
        """)
        distribution = cursor.fetchone()
        
        cursor.close()
        
        return {
            "total_reports": total_reports,
            "unused_reports": unused_reports,
            "scam_reports": distribution[0] if distribution else 0,
            "legitimate_reports": distribution[1] if distribution else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training data error: {str(e)}")


@router.post("/trigger-fraud-ring-detection")
async def trigger_fraud_ring_detection(
    authorized: bool = Depends(verify_admin_token)
):
    """Manually trigger fraud ring detection."""
    try:
        # Load scam reports from database
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT features, reported_at
            FROM scam_reports
            WHERE is_scam = TRUE
            ORDER BY reported_at DESC
            LIMIT 1000
        """)
        
        reports = cursor.fetchall()
        cursor.close()
        
        # Add to fraud detector graph
        for i, (features, timestamp) in enumerate(reports):
            sender_id = f"sender_{i}"  # In production, extract from metadata
            fraud_detector.add_scam_report(sender_id, features, timestamp, True)
        
        # Detect rings
        rings = fraud_detector.detect_fraud_rings()
        
        # Save to database
        fraud_detector.save_rings_to_database(rings)
        
        # Get statistics
        stats = fraud_detector.get_ring_statistics()
        
        return {
            "success": True,
            "rings_detected": len(rings),
            "statistics": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.get("/daily-metrics")
async def get_daily_metrics(
    days: int = 7,
    authorized: bool = Depends(verify_admin_token)
):
    """Get daily metrics for the last N days."""
    try:
        cursor = db.conn.cursor()
        
        cursor.execute("""
            SELECT 
                metric_date, total_scans, scams_detected,
                free_tier_scans, pro_tier_scans, avg_response_time_ms
            FROM daily_metrics
            WHERE metric_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY metric_date DESC
        """, (days,))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                "date": row[0].isoformat(),
                "total_scans": row[1],
                "scams_detected": row[2],
                "free_tier_scans": row[3],
                "pro_tier_scans": row[4],
                "avg_response_time_ms": row[5]
            })
        
        cursor.close()
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily metrics error: {str(e)}")
