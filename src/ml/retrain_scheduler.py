"""
Weekly Model Retraining Scheduler
Automatically retrains XGBoost model with new user feedback data
"""

import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import DatabaseService


def retrain_model():
    """Execute model retraining."""
    print("\n" + "="*60)
    print(f"🔄 WEEKLY MODEL RETRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check if we have new training data
    db = DatabaseService()
    reports = db.get_training_data(limit=1, unused_only=True)
    
    if not reports:
        print("⚠️  No new training data since last training")
        print("   Skipping retraining...")
        db.close()
        return
    
    print(f"✅ Found new training data, starting retraining...")
    
    # Run training script
    train_script = Path(__file__).parent / 'train_model.py'
    
    try:
        result = subprocess.run(
            [sys.executable, str(train_script)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Model retraining completed successfully")
        else:
            print(f"❌ Model retraining failed with code {result.returncode}")
            print(result.stderr)
    
    except subprocess.TimeoutExpired:
        print("❌ Model retraining timed out (>10 minutes)")
    except Exception as e:
        print(f"❌ Model retraining error: {e}")
    
    db.close()
    print("="*60 + "\n")


def main():
    """Main scheduler loop."""
    print("🤖 UniversalShield Model Retraining Scheduler")
    print("   Schedule: Every Sunday at 2:00 AM")
    print("   Press Ctrl+C to stop\n")
    
    # Schedule weekly retraining (every Sunday at 2 AM)
    schedule.every().sunday.at("02:00").do(retrain_model)
    
    # For testing: uncomment to run every 5 minutes
    # schedule.every(5).minutes.do(retrain_model)
    
    print("✅ Scheduler started. Waiting for scheduled time...\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")


if __name__ == "__main__":
    main()
