#!/bin/bash

# 🧪 Fraud Detection Agent - Comprehensive Test Runner
# This script runs all Python tests with coverage and performance metrics

echo "🧪 Starting Fraud Detection Agent Test Suite"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run tests with coverage
run_tests_with_coverage() {
    local test_name="$1"
    local test_path="$2"
    
    print_status "Running $test_name with coverage..."
    
    if python -m pytest "$test_path" -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml; then
        print_success "$test_name tests passed! ✅"
        return 0
    else
        print_error "$test_name tests failed! ❌"
        return 1
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    if python -m pytest tests/test_api_controller.py::TestAPIController::test_response_time_performance -v; then
        print_success "Performance tests passed! ✅"
    else
        print_error "Performance tests failed! ❌"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    if python -m pytest tests/test_api_controller.py -v -m integration; then
        print_success "Integration tests passed! ✅"
    else
        print_error "Integration tests failed! ❌"
        return 1
    fi
}

# Function to generate test report
generate_test_report() {
    print_status "Generating comprehensive test report..."
    
    # Run all tests with coverage
    python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml --junitxml=test-results.xml
    
    if [ $? -eq 0 ]; then
        print_success "Test report generated successfully! ✅"
        print_status "Coverage report available at: htmlcov/index.html"
        print_status "JUnit XML report available at: test-results.xml"
    else
        print_error "Test report generation failed! ❌"
        return 1
    fi
}

# Main test execution
main() {
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    print_status "Fraud Detection Agent - Python Test Suite"
    print_status "All major services and endpoints tested"
    echo ""
    
    # Test 1: Investment Fraud Detection Service
    echo "🏗️ PHASE 1: INVESTMENT FRAUD DETECTION SERVICE"
    echo "=============================================="
    if run_tests_with_coverage "Investment Fraud Detection Service" "tests/test_investment_fraud_service.py"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 2: ML Service
    echo "🤖 PHASE 2: ML SERVICE"
    echo "====================="
    if run_tests_with_coverage "ML Service" "tests/test_ml_service.py"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 3: Fraud Tools Service
    echo "🔧 PHASE 3: FRAUD TOOLS SERVICE"
    echo "==============================="
    if run_tests_with_coverage "Fraud Tools Service" "tests/test_fraud_tools_service.py"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 4: API Controller
    echo "🔌 PHASE 4: API CONTROLLER"
    echo "========================="
    if run_tests_with_coverage "API Controller" "tests/test_api_controller.py"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 5: Performance Tests
    echo "📈 PHASE 5: PERFORMANCE TESTS"
    echo "============================="
    if run_performance_tests; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 6: Integration Tests
    echo "🔗 PHASE 6: INTEGRATION TESTS"
    echo "============================="
    if run_integration_tests; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Test 7: Complete Test Suite
    echo "📊 PHASE 7: COMPLETE TEST SUITE"
    echo "==============================="
    if generate_test_report; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    echo ""
    
    # Summary
    echo "📋 TEST SUMMARY"
    echo "==============="
    print_status "Total test phases: $total_tests"
    print_success "Passed: $passed_tests"
    if [ $failed_tests -gt 0 ]; then
        print_error "Failed: $failed_tests"
    else
        print_success "Failed: $failed_tests"
    fi
    
    if [ $failed_tests -eq 0 ]; then
        print_success "🎉 All tests passed! The Python fraud detection agent is working perfectly!"
        echo ""
        print_status "✅ Investment Fraud Detection Service: Fully functional"
        print_status "✅ ML Service with XGBoost and Neural Networks: Fully functional"
        print_status "✅ Fraud Tools Service with risk assessment: Fully functional"
        print_status "✅ API Controller with 50+ endpoints: Fully functional"
        print_status "✅ Performance tests: All passing"
        print_status "✅ Integration tests: All passing"
        echo ""
        print_success "🚀 The Python fraud detection agent is ready for production!"
        exit 0
    else
        print_error "❌ Some tests failed. Please review the output above."
        exit 1
    fi
}

# Run main function
main "$@"
