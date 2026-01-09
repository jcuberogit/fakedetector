"""
Integration Test Suite for UniversalShield
Tests all components end-to-end before deployment
"""

import sys
import json
import requests
from pathlib import Path
import subprocess
import time

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"{GREEN}✅ PASS{RESET}: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"{RED}❌ FAIL{RESET}: {test_name}")
        print(f"   Error: {error}")
    
    def add_warning(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"{YELLOW}⚠️  WARN{RESET}: {test_name}")
        print(f"   {message}")
    
    def summary(self):
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"{GREEN}Passed: {len(self.passed)}{RESET}")
        print(f"{RED}Failed: {len(self.failed)}{RESET}")
        print(f"{YELLOW}Warnings: {len(self.warnings)}{RESET}")
        
        if self.failed:
            print(f"\n{RED}Failed Tests:{RESET}")
            for name, error in self.failed:
                print(f"  - {name}: {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for name, msg in self.warnings:
                print(f"  - {name}: {msg}")
        
        print("\n" + "="*60)
        
        if len(self.failed) == 0:
            print(f"{GREEN}✅ ALL TESTS PASSED - READY FOR DEPLOYMENT{RESET}")
            return True
        else:
            print(f"{RED}❌ TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT{RESET}")
            return False


def test_file_structure(results):
    """Test that all required files exist."""
    print(f"\n{BLUE}Testing File Structure...{RESET}")
    
    base_path = Path(__file__).parent.parent
    
    required_files = [
        # Backend
        'src/contextual/analyzer.py',
        'src/contextual/feature_extractor.py',
        'src/api/scam_detection_api.py',
        'src/api/subscription_api.py',
        'src/ml/train_model.py',
        'src/ml/ml_service.py',
        
        # Extension
        'extensions/UniversalShield/src/localAnalyzer.js',
        'extensions/UniversalShield/src/cloudAnalyzer.js',
        'extensions/UniversalShield/src/badge.js',
        'extensions/UniversalShield/src/badge.css',
        'extensions/UniversalShield/manifest.json',
        
        # Data & Tests
        'data/scam_examples.json',
        'tests/test_contextual_analyzer.py',
        
        # Documentation
        'README.md',
        'PRIVACY_POLICY.md',
        'requirements.txt',
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            results.add_pass(f"File exists: {file_path}")
        else:
            results.add_fail(f"File missing: {file_path}", "File not found")


def test_python_imports(results):
    """Test that all Python modules can be imported."""
    print(f"\n{BLUE}Testing Python Imports...{RESET}")
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    imports = [
        ('src.contextual.analyzer', 'ContextualAnalyzer'),
        ('src.contextual.feature_extractor', 'PrivacyFirstFeatureExtractor'),
        ('src.ml.ml_service', 'MLService'),
    ]
    
    for module_name, class_name in imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            results.add_pass(f"Import: {module_name}.{class_name}")
        except Exception as e:
            results.add_fail(f"Import: {module_name}.{class_name}", str(e))


def test_contextual_analyzer(results):
    """Test the contextual analyzer with sample data."""
    print(f"\n{BLUE}Testing Contextual Analyzer...{RESET}")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.contextual.analyzer import ContextualAnalyzer
        
        analyzer = ContextualAnalyzer()
        
        # Test scam message
        scam_message = "URGENT! Download this file.exe immediately for your job interview!"
        scam_metadata = {
            'platform': 'linkedin',
            'sender_account_age_days': 2,
            'connection_degree': 3,
            'file_type': 'exe',
            'has_attachment': True,
            'previous_interactions': 0
        }
        
        analysis = analyzer.analyze(scam_message, scam_metadata)
        
        if analysis['risk_score'] >= 70:
            results.add_pass("Contextual Analyzer: Detects scam (score >= 70)")
        else:
            results.add_fail("Contextual Analyzer: Failed to detect scam", 
                           f"Score: {analysis['risk_score']}, expected >= 70")
        
        # Test safe message
        safe_message = "Thanks for connecting! Looking forward to staying in touch."
        safe_metadata = {
            'platform': 'linkedin',
            'sender_account_age_days': 365,
            'connection_degree': 2,
            'has_attachment': False,
            'previous_interactions': 5
        }
        
        analysis = analyzer.analyze(safe_message, safe_metadata)
        
        if analysis['risk_score'] < 30:
            results.add_pass("Contextual Analyzer: Identifies safe message (score < 30)")
        else:
            results.add_warning("Contextual Analyzer: Safe message scored too high",
                              f"Score: {analysis['risk_score']}, expected < 30")
        
    except Exception as e:
        results.add_fail("Contextual Analyzer", str(e))


def test_feature_extractor(results):
    """Test the privacy-first feature extractor."""
    print(f"\n{BLUE}Testing Feature Extractor...{RESET}")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.contextual.feature_extractor import PrivacyFirstFeatureExtractor
        
        extractor = PrivacyFirstFeatureExtractor()
        
        message = "Click here NOW to claim your prize!"
        metadata = {
            'platform': 'gmail',
            'sender_account_age_days': 1,
            'connection_degree': 3,
            'has_attachment': False
        }
        
        features = extractor.extract_features(message, metadata)
        
        # Verify no PII in features
        has_pii = False
        for key, value in features.items():
            if isinstance(value, str) and len(value) > 10:
                has_pii = True
                break
        
        if not has_pii:
            results.add_pass("Feature Extractor: No PII in features (privacy-first)")
        else:
            results.add_fail("Feature Extractor: Contains PII", "Found string values in features")
        
        # Verify required features
        required_features = [
            'message_length', 'urgency_keywords_count', 'sender_account_age_days',
            'file_extension_risk', 'platform_id'
        ]
        
        missing = [f for f in required_features if f not in features]
        if not missing:
            results.add_pass("Feature Extractor: All required features present")
        else:
            results.add_fail("Feature Extractor: Missing features", f"Missing: {missing}")
        
    except Exception as e:
        results.add_fail("Feature Extractor", str(e))


def test_scam_dataset(results):
    """Test that scam examples dataset is valid."""
    print(f"\n{BLUE}Testing Scam Dataset...{RESET}")
    
    try:
        data_path = Path(__file__).parent.parent / 'data' / 'scam_examples.json'
        
        with open(data_path, 'r') as f:
            examples = json.load(f)
        
        if len(examples) >= 20:
            results.add_pass(f"Scam Dataset: Contains {len(examples)} examples")
        else:
            results.add_fail("Scam Dataset: Too few examples", f"Found {len(examples)}, need >= 20")
        
        # Verify structure
        scam_count = sum(1 for e in examples if e.get('is_scam'))
        safe_count = len(examples) - scam_count
        
        if scam_count >= 10 and safe_count >= 5:
            results.add_pass(f"Scam Dataset: Balanced ({scam_count} scams, {safe_count} safe)")
        else:
            results.add_warning("Scam Dataset: Imbalanced", 
                              f"{scam_count} scams, {safe_count} safe")
        
    except Exception as e:
        results.add_fail("Scam Dataset", str(e))


def test_api_server_start(results):
    """Test if API server can start (doesn't actually start it)."""
    print(f"\n{BLUE}Testing API Configuration...{RESET}")
    
    try:
        # Check if FastAPI is installed
        import fastapi
        results.add_pass("API: FastAPI installed")
        
        # Check if uvicorn is installed
        import uvicorn
        results.add_pass("API: Uvicorn installed")
        
        # Try to import the API
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.api import scam_detection_api
        results.add_pass("API: scam_detection_api module loads")
        
    except ImportError as e:
        results.add_fail("API Dependencies", str(e))
    except Exception as e:
        results.add_fail("API Configuration", str(e))


def test_extension_manifest(results):
    """Test that extension manifest is valid."""
    print(f"\n{BLUE}Testing Extension Manifest...{RESET}")
    
    try:
        manifest_path = Path(__file__).parent.parent / 'extensions/UniversalShield/manifest.json'
        
        if not manifest_path.exists():
            results.add_fail("Extension Manifest", "manifest.json not found")
            return
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ['manifest_version', 'name', 'version', 'description']
        missing = [f for f in required_fields if f not in manifest]
        
        if not missing:
            results.add_pass("Extension Manifest: All required fields present")
        else:
            results.add_fail("Extension Manifest: Missing fields", f"Missing: {missing}")
        
        # Check manifest version
        if manifest.get('manifest_version') == 3:
            results.add_pass("Extension Manifest: Using Manifest V3")
        else:
            results.add_fail("Extension Manifest: Wrong version", 
                           f"Expected 3, got {manifest.get('manifest_version')}")
        
    except json.JSONDecodeError as e:
        results.add_fail("Extension Manifest: Invalid JSON", str(e))
    except Exception as e:
        results.add_fail("Extension Manifest", str(e))


def test_documentation(results):
    """Test that documentation is complete."""
    print(f"\n{BLUE}Testing Documentation...{RESET}")
    
    base_path = Path(__file__).parent.parent
    
    docs = {
        'README.md': 'Project documentation',
        'PRIVACY_POLICY.md': 'Privacy policy',
        'docs/PAYPAL_SETUP_GUIDE.md': 'PayPal setup guide',
        'docs/CHROME_WEB_STORE_GUIDE.md': 'Chrome Web Store guide',
        'docs/DEPLOYMENT_GUIDE.md': 'Deployment guide'
    }
    
    for doc_path, description in docs.items():
        full_path = base_path / doc_path
        if full_path.exists():
            size = full_path.stat().st_size
            if size > 1000:  # At least 1KB
                results.add_pass(f"Documentation: {description} ({size} bytes)")
            else:
                results.add_warning(f"Documentation: {description}", "File seems too small")
        else:
            results.add_fail(f"Documentation: {description}", "File not found")


def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("UNIVERSALSHIELD INTEGRATION TEST SUITE")
    print("="*60)
    
    results = TestResults()
    
    # Run all tests
    test_file_structure(results)
    test_python_imports(results)
    test_contextual_analyzer(results)
    test_feature_extractor(results)
    test_scam_dataset(results)
    test_api_server_start(results)
    test_extension_manifest(results)
    test_documentation(results)
    
    # Print summary
    success = results.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
