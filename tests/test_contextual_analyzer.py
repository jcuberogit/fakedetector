"""
Test suite for Contextual Analyzer
Validates that the analyzer achieves >85% precision on scam detection
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.contextual.analyzer import ContextualAnalyzer


def load_scam_examples():
    """Load test dataset."""
    data_path = Path(__file__).parent.parent / 'data' / 'scam_examples.json'
    with open(data_path, 'r') as f:
        return json.load(f)


def test_analyzer():
    """Test analyzer on all examples and calculate metrics."""
    analyzer = ContextualAnalyzer()
    examples = load_scam_examples()
    
    results = {
        'total': len(examples),
        'correct': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'true_positives': 0,
        'true_negatives': 0,
        'details': []
    }
    
    for example in examples:
        analysis = analyzer.analyze(example['message'], example['metadata'])
        
        is_scam = example['is_scam']
        detected_as_scam = analysis['risk_score'] >= 70
        
        # Calculate confusion matrix
        if is_scam and detected_as_scam:
            results['true_positives'] += 1
            results['correct'] += 1
        elif not is_scam and not detected_as_scam:
            results['true_negatives'] += 1
            results['correct'] += 1
        elif not is_scam and detected_as_scam:
            results['false_positives'] += 1
        elif is_scam and not detected_as_scam:
            results['false_negatives'] += 1
        
        # Store details
        results['details'].append({
            'id': example['id'],
            'is_scam': is_scam,
            'detected_as_scam': detected_as_scam,
            'risk_score': analysis['risk_score'],
            'expected_score': example.get('expected_risk_score', 0),
            'correct': (is_scam == detected_as_scam)
        })
    
    # Calculate metrics
    accuracy = results['correct'] / results['total']
    
    precision = 0
    if (results['true_positives'] + results['false_positives']) > 0:
        precision = results['true_positives'] / (results['true_positives'] + results['false_positives'])
    
    recall = 0
    if (results['true_positives'] + results['false_negatives']) > 0:
        recall = results['true_positives'] / (results['true_positives'] + results['false_negatives'])
    
    f1_score = 0
    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'confusion_matrix': {
            'true_positives': results['true_positives'],
            'true_negatives': results['true_negatives'],
            'false_positives': results['false_positives'],
            'false_negatives': results['false_negatives']
        },
        'details': results['details']
    }


def print_results(metrics):
    """Print test results."""
    print("\n" + "="*60)
    print("UNIVERSALSHIELD CONTEXTUAL ANALYZER TEST RESULTS")
    print("="*60)
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Accuracy:  {metrics['accuracy']:.1%} ({'✅ PASS' if metrics['accuracy'] >= 0.85 else '❌ FAIL'})")
    print(f"   Precision: {metrics['precision']:.1%} ({'✅ PASS' if metrics['precision'] >= 0.85 else '❌ FAIL'})")
    print(f"   Recall:    {metrics['recall']:.1%} ({'✅ PASS' if metrics['recall'] >= 0.80 else '❌ FAIL'})")
    print(f"   F1 Score:  {metrics['f1_score']:.1%}")
    
    cm = metrics['confusion_matrix']
    print(f"\n🔍 Confusion Matrix:")
    print(f"   True Positives:  {cm['true_positives']} (scams correctly detected)")
    print(f"   True Negatives:  {cm['true_negatives']} (safe messages correctly identified)")
    print(f"   False Positives: {cm['false_positives']} (safe messages flagged as scams)")
    print(f"   False Negatives: {cm['false_negatives']} (scams missed)")
    
    # Show failed cases
    failed_cases = [d for d in metrics['details'] if not d['correct']]
    if failed_cases:
        print(f"\n⚠️  Failed Cases ({len(failed_cases)}):")
        for case in failed_cases:
            status = "False Positive" if not case['is_scam'] else "False Negative"
            print(f"   ID {case['id']}: {status} (score: {case['risk_score']}, expected: {case['expected_score']})")
    
    # Overall assessment
    print(f"\n{'='*60}")
    target_met = metrics['precision'] >= 0.85 and metrics['recall'] >= 0.80
    if target_met:
        print("✅ TARGET MET: Contextual Intelligence validated!")
        print("   Ready for production deployment.")
    else:
        print("❌ TARGET NOT MET: Needs improvement")
        print("   Review failed cases and adjust scoring weights.")
    print("="*60 + "\n")
    
    return target_met


if __name__ == "__main__":
    print("Running Contextual Analyzer validation tests...")
    metrics = test_analyzer()
    target_met = print_results(metrics)
    
    # Exit with appropriate code
    sys.exit(0 if target_met else 1)
