"""
XGBoost Model Training for Scam Detection
Trains on anonymized features from scam examples dataset
"""

import json
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from xgboost import XGBClassifier
import joblib
import sys
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.contextual.feature_extractor import PrivacyFirstFeatureExtractor
from src.db.database import DatabaseService


def load_dataset_from_db(db: DatabaseService, limit: int = 10000):
    """Load training data from database (user feedback)."""
    print("\n📥 Loading training data from database...")
    
    reports = db.get_training_data(limit=limit, unused_only=False)
    
    if not reports:
        print("⚠️  No training data found in database")
        return None, None, None
    
    X = []
    y = []
    
    for report in reports:
        features = report['features']
        
        # Convert to feature vector (34 features now)
        feature_vector = [
            features.get('message_length', 0),
            features.get('word_count', 0),
            features.get('sentence_count', 1),
            features.get('avg_word_length', 5.0),
            features.get('urgency_keywords_count', 0),
            features.get('money_keywords_count', 0),
            features.get('credential_keywords_count', 0),
            features.get('link_count', 0),
            features.get('has_shortened_url', 0),
            features.get('file_attachment', 0),
            features.get('file_extension_risk', 0.0),
            features.get('exclamation_count', 0),
            features.get('question_count', 0),
            features.get('caps_ratio', 0.0),
            features.get('number_count', 0),
            features.get('currency_symbol_count', 0),
            features.get('sender_account_age_days', 365),
            features.get('connection_degree', 3),
            features.get('previous_interactions', 0),
            features.get('platform_id', 0),
            features.get('context_type_id', 0),
            features.get('requests_download', 0),
            features.get('requests_payment', 0),
            features.get('requests_credentials', 0),
            features.get('has_urgency', 0),
            # Rachel Good pattern features
            features.get('recruiter_keywords_count', 0),
            features.get('location_inquiry', 0),
            features.get('experience_inquiry', 0),
            features.get('gmail_recruiter_combo', 0),
            features.get('vague_address_pattern', 0),
            # Financial phishing features
            features.get('financial_phishing_keywords_count', 0),
            features.get('credit_card_mention', 0),
            features.get('credit_limit_mention', 0),
            features.get('security_deposit_mention', 0)
        ]
        
        X.append(feature_vector)
        y.append(1 if report['is_scam'] else 0)
    
    print(f"✅ Loaded {len(reports)} labeled samples from database")
    return np.array(X), np.array(y), reports


def load_dataset_from_json():
    """Load scam examples from JSON file (fallback/initial training)."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'scam_examples.json'
    
    if not data_path.exists():
        print(f"⚠️  No JSON dataset found at {data_path}")
        return None, None, None
    
    with open(data_path, 'r') as f:
        examples = json.load(f)
    
    extractor = PrivacyFirstFeatureExtractor()
    
    X = []
    y = []
    
    for example in examples:
        # Extract anonymized features
        features = extractor.extract_features(example['message'], example['metadata'])
        
        # Convert to feature vector (34 features)
        feature_vector = [
            features['message_length'],
            features['word_count'],
            features['sentence_count'],
            features['avg_word_length'],
            features['urgency_keywords_count'],
            features['money_keywords_count'],
            features['credential_keywords_count'],
            features['link_count'],
            features['has_shortened_url'],
            features['file_attachment'],
            features['file_extension_risk'],
            features['exclamation_count'],
            features['question_count'],
            features['caps_ratio'],
            features['number_count'],
            features['currency_symbol_count'],
            features['sender_account_age_days'],
            features['connection_degree'],
            features['previous_interactions'],
            features['platform_id'],
            features['context_type_id'],
            features['requests_download'],
            features['requests_payment'],
            features['requests_credentials'],
            features['has_urgency'],
            # Rachel Good pattern features
            features['recruiter_keywords_count'],
            features['location_inquiry'],
            features['experience_inquiry'],
            features['gmail_recruiter_combo'],
            features['vague_address_pattern'],
            # Financial phishing features
            features['financial_phishing_keywords_count'],
            features['credit_card_mention'],
            features['credit_limit_mention'],
            features['security_deposit_mention']
        ]
        
        X.append(feature_vector)
        y.append(1 if example['is_scam'] else 0)
    
    return np.array(X), np.array(y), examples


def train_model(X, y):
    """Train XGBoost classifier."""
    print("\n" + "="*60)
    print("TRAINING XGBOOST SCAM DETECTION MODEL")
    print("="*60)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"\n📊 Dataset Split:")
    print(f"   Training samples: {len(X_train)} ({sum(y_train)} scams, {len(y_train)-sum(y_train)} safe)")
    print(f"   Test samples: {len(X_test)} ({sum(y_test)} scams, {len(y_test)-sum(y_test)} safe)")
    
    # Train model
    print(f"\n🔧 Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average='binary'
    )
    
    print(f"\n📈 Test Set Performance:")
    print(f"   Precision: {precision:.1%} ({'✅ PASS' if precision >= 0.85 else '❌ FAIL'})")
    print(f"   Recall:    {recall:.1%} ({'✅ PASS' if recall >= 0.80 else '❌ FAIL'})")
    print(f"   F1 Score:  {f1:.1%}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n🔍 Confusion Matrix:")
    print(f"   True Negatives:  {cm[0][0]} (safe correctly identified)")
    print(f"   False Positives: {cm[0][1]} (safe flagged as scam)")
    print(f"   False Negatives: {cm[1][0]} (scams missed)")
    print(f"   True Positives:  {cm[1][1]} (scams correctly detected)")
    
    # Cross-validation
    print(f"\n🔄 5-Fold Cross-Validation:")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='precision')
    print(f"   Mean Precision: {cv_scores.mean():.1%} (+/- {cv_scores.std():.1%})")
    
    # Feature importance
    print(f"\n🎯 Top 10 Most Important Features:")
    feature_names = [
        'message_length', 'word_count', 'sentence_count', 'avg_word_length',
        'urgency_keywords', 'money_keywords', 'credential_keywords', 'link_count',
        'has_shortened_url', 'file_attachment', 'file_extension_risk', 'exclamation_count',
        'question_count', 'caps_ratio', 'number_count', 'currency_symbol_count',
        'sender_account_age', 'connection_degree', 'previous_interactions',
        'platform_id', 'context_type_id', 'requests_download', 'requests_payment',
        'requests_credentials', 'has_urgency',
        # Rachel Good features
        'recruiter_keywords', 'location_inquiry', 'experience_inquiry',
        'gmail_recruiter_combo', 'vague_address_pattern',
        # Financial phishing features
        'financial_phishing_keywords', 'credit_card_mention', 'credit_limit_mention',
        'security_deposit_mention'
    ]
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    
    for i, idx in enumerate(indices, 1):
        print(f"   {i}. {feature_names[idx]}: {importances[idx]:.3f}")
    
    return model, precision, recall, f1


def save_model(model):
    """Save trained model."""
    models_dir = Path(__file__).parent.parent.parent / 'models'
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / 'scam_detector_v1.pkl'
    joblib.dump(model, model_path)
    
    print(f"\n💾 Model saved to: {model_path}")
    return model_path


def main():
    """Main training pipeline."""
    # Initialize database
    db = DatabaseService()
    
    # Load data (try database first, fallback to JSON)
    print("Loading dataset...")
    X, y, data_source = load_dataset_from_db(db, limit=10000)
    
    if X is None:
        print("\n⚠️  No database data, trying JSON file...")
        X, y, data_source = load_dataset_from_json()
    
    if X is None or len(X) == 0:
        print("\n❌ ERROR: No training data available")
        print("   Please either:")
        print("   1. Add scam reports via /api/v1/report-scam endpoint")
        print("   2. Create data/scam_examples.json with labeled examples")
        return 1
    
    print(f"\nLoaded {len(X)} examples ({sum(y)} scams, {len(y)-sum(y)} safe)")
    print(f"Feature count: {X.shape[1]} (expected: 34)")
    
    # Train model
    model, precision, recall, f1 = train_model(X, y)
    
    # Save model
    model_path = save_model(model)
    
    # Save model version to database
    version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    metrics = {
        'accuracy': (precision + recall) / 2,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
    
    model_id = db.save_model_version(
        version=version,
        model_type='xgboost',
        training_samples=len(X),
        metrics=metrics,
        model_path=str(model_path),
        feature_count=X.shape[1]
    )
    
    if model_id:
        print(f"\n💾 Model version saved to database: {version} (ID: {model_id})")
        
        # Optionally set as active
        user_input = input("\nSet this model as active? (y/n): ")
        if user_input.lower() == 'y':
            db.set_active_model(model_id)
            print(f"✅ Model {version} is now active")
    
    # Final assessment
    print("\n" + "="*60)
    target_met = precision >= 0.85 and recall >= 0.80
    if target_met:
        print("✅ TARGET MET: Model ready for production!")
        print(f"   Precision: {precision:.1%} (target: ≥85%)")
        print(f"   Recall: {recall:.1%} (target: ≥80%)")
        print(f"   F1 Score: {f1:.1%}")
    else:
        print("❌ TARGET NOT MET: Model needs improvement")
        print(f"   Precision: {precision:.1%} (target: ≥85%)")
        print(f"   Recall: {recall:.1%} (target: ≥80%)")
    print("="*60 + "\n")
    
    db.close()
    return 0 if target_met else 1


if __name__ == "__main__":
    sys.exit(main())
