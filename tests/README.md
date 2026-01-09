# Fraud Detection Agent Test Suite

## Overview

Comprehensive test suite for the Fraud Detection Agent following TDD methodology (RED → GREEN → REFACTOR).

## Test Structure

```
tests/
├── unit/              # Unit tests for individual services
│   ├── test_fraud_tools.py
│   ├── test_rules_engine.py
│   └── test_investment_fraud.py
├── integration/       # Integration tests
├── ml/                # ML model tests
│   ├── test_ml_models_accuracy.py
│   └── test_gnn_fraud_rings.py
├── api/               # API endpoint tests
│   └── test_fraud_agent_api.py
└── fixtures/          # Test fixtures and data
```

## Running Tests

### Run all tests
```bash
cd /Users/jcubero/ParadigmStore/agents/paradigm.fraud.agent
python3 -m pytest tests/ -v
```

### Run with coverage
```bash
python3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Run specific test file
```bash
python3 -m pytest tests/unit/test_fraud_tools.py -v
```

### Run by marker
```bash
python3 -m pytest -m unit -v
python3 -m pytest -m ml -v
python3 -m pytest -m api -v
```

## Test Coverage Goals

- **Current**: <5% (only conftest.py existed)
- **Target**: 60%+ (per requirements)
- **Long-term**: 80%+ (per FRAUD-001 ticket)

## Critical Tests

### FRAUD-001: Test Infrastructure ✅
- Test directory structure created
- pytest.ini configured with coverage
- conftest.py with fixtures

### FRAUD-002: ML Model Accuracy Tests
- Target: >99% accuracy
- False positive rate: <1%
- False negative rate: <0.1%

### FRAUD-003: GNN Fraud Ring Detection
- Test known fraud ring patterns
- Test legitimate connections (no false positives)
- Community detection

### FRAUD-004: Rules Engine Tests
- Test all static rules
- Test dynamic rule creation/update/delete
- Test rule combinations and priority

### FRAUD-005: Hardcoded Path Fix ✅
- Fixed line 20 in agent.py
- Uses Path(__file__) for relative paths

## Dependencies

Install test dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pytest==7.4.2
- pytest-asyncio==0.21.1
- pytest-cov==4.1.0
- pytest-mock==3.12.0
- networkx==3.2.1

## Notes

- Tests follow TDD methodology (RED → GREEN → REFACTOR)
- All async tests use `@pytest.mark.asyncio`
- Tests use fixtures from conftest.py
- Mock external services where appropriate










