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

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.contextual.feature_extractor import PrivacyFirstFeatureExtractor


def load_dataset():
    """Load scam examples and extract features."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'scam_examples.json'
    
    with open(data_path, 'r') as f:
        examples = json.load(f)
    
    extractor = PrivacyFirstFeatureExtractor()
    
    X = []
    y = []
    
    for example in examples:
        # Extract anonymized features
        features = extractor.extract_features(example['message'], example['metadata'])
        
        # Convert to feature vector
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
            features['has_urgency']
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
        'requests_credentials', 'has_urgency'
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
    # Load data
    print("Loading dataset...")
    X, y, examples = load_dataset()
    
    print(f"Loaded {len(examples)} examples ({sum(y)} scams, {len(y)-sum(y)} safe)")
    
    # Train model
    model, precision, recall, f1 = train_model(X, y)
    
    # Save model
    model_path = save_model(model)
    
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
    
    return 0 if target_met else 1


if __name__ == "__main__":
    sys.exit(main())
