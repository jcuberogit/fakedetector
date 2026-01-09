#!/usr/bin/env python3
"""
Universal Fraud Detection SDK Setup Script
Installs and configures the SDK for development and production use
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.info(f"❌ {description} failed: {e}")
        if e.stdout:
            logger.info(f"   stdout: {e.stdout}")
        if e.stderr:
            logger.info(f"   stderr: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    logger.info("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.info(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies"""
    logger.info("\n📦 Installing Python dependencies...")
    
    # Install core dependencies
    core_deps = [
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "requests>=2.28.0",
        "python-jose>=3.3.0",
        "cryptography>=3.4.8"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    # Install development dependencies if in development mode
    if os.getenv("SDK_DEV_MODE", "false").lower() == "true":
        dev_deps = [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991"
        ]
        
        for dep in dev_deps:
            if not run_command(f"pip install {dep}", f"Installing dev dependency {dep}"):
                return False
    
    return True


def create_directories():
    """Create necessary directories"""
    logger.info("\n📁 Creating directories...")
    
    directories = [
        "logs",
        "cache",
        "storage",
        "tests",
        "examples"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {dir_name}")
        else:
            logger.info(f"ℹ️  Directory already exists: {dir_name}")
    
    return True


def setup_logging():
    """Setup logging configuration"""
    logger.info("\n📝 Setting up logging...")
    
    log_config = """
import logging
import os
from pathlib import Path

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'sdk.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set SDK logger level
    sdk_logger = logging.getLogger('sdk')
    sdk_logger.setLevel(logging.INFO)
    
    return sdk_logger
"""
    
    with open("logging_config.py", "w") as f:
        f.write(log_config)
    
    logger.info("✅ Logging configuration created")
    return True


def create_config_file():
    """Create default configuration file"""
    logger.info("\n⚙️ Creating configuration file...")
    
    config_content = """
# Universal Fraud Detection SDK Configuration
# Copy this file to config.py and modify as needed

import os
from sdk import FraudDetectionSdkOptions

# Default configuration
DEFAULT_CONFIG = FraudDetectionSdkOptions(
    BaseUrl=os.getenv("FRAUD_API_BASE_URL", "http://localhost:5000"),
    Environment=os.getenv("SDK_ENVIRONMENT", "development"),
    Timeout=float(os.getenv("SDK_TIMEOUT", "30.0")),
    ApplicationName=os.getenv("SDK_APP_NAME", "FraudDetectionApp"),
    ApplicationVersion=os.getenv("SDK_APP_VERSION", "1.0.0")
)

# Test configuration
TEST_CONFIG = FraudDetectionSdkOptions(
    BaseUrl="https://test-fraudapi.paradigmstore.com",
    Environment="test",
    Timeout=10.0
)

# Production configuration
PRODUCTION_CONFIG = FraudDetectionSdkOptions(
    BaseUrl="https://fraudapi.paradigmstore.com",
    Environment="production",
    Timeout=30.0
)
"""
    
    with open("config_template.py", "w") as f:
        f.write(config_content)
    
    logger.info("✅ Configuration template created")
    return True


def run_tests():
    """Run SDK tests"""
    logger.info("\n🧪 Running SDK tests...")
    
    if not run_command("python -m pytest test_sdk.py -v", "Running SDK tests"):
        logger.info("⚠️  Some tests failed, but SDK setup can continue")
        return True
    
    return True


def create_example_scripts():
    """Create example scripts"""
    logger.info("\n📚 Creating example scripts...")
    
    # Basic usage example
    basic_example = '''#!/usr/bin/env python3
"""
Basic SDK Usage Example
"""

import asyncio
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, MobileChatRequest

async def main():
    # Initialize SDK
    options = FraudDetectionSdkOptions(
        BaseUrl="http://localhost:5000",
        Environment="development"
    )
    
    async with FraudDetectionSdk(options) as sdk:
        # Send a chat message
        request = MobileChatRequest(
            Message="Is this transaction safe?"
        )
        
        response = await sdk.chat_async(request)
        logger.info(f"Response: {response.message}")
        logger.info(f"Risk Score: {response.risk_score}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("examples/basic_usage.py", "w") as f:
        f.write(basic_example)
    
    # Make executable
    os.chmod("examples/basic_usage.py", 0o755)
    
    logger.info("✅ Example scripts created")
    return True


def print_setup_summary():
    """Print setup summary"""
    logger.info("\n" + "="*60)
    logger.info("🎉 Universal Fraud Detection SDK Setup Complete!")
    logger.info("="*60)
    logger.info("\n📋 Next Steps:")
    logger.info("1. Copy config_template.py to config.py and modify as needed")
    logger.info("2. Run examples/basic_usage.py to test the SDK")
    logger.info("3. Check logs/sdk.log for any issues")
    logger.info("4. Read README.md for detailed documentation")
    logger.info("\n🔧 Development Mode:")
    logger.info("   Set SDK_DEV_MODE=true to install development dependencies")
    logger.info("\n🌐 Integration:")
    logger.info("   The SDK is ready to integrate with your fraud detection agent")
    logger.info("   Make sure the agent is running on the configured BaseUrl")
    logger.info("\n📚 Documentation:")
    logger.info("   - README.md: Quick start guide")
    logger.info("   - integration_example.py: Comprehensive examples")
    logger.info("   - test_sdk.py: Test suite")
    logger.info("\n🆘 Support:")
    logger.info("   - GitHub Issues: https://github.com/paradigmstore/fraud-detection-sdk/issues")
    logger.info("   - Email: support@paradigmstore.com")


def main():
    """Main setup function"""
    logger.info("🛡️ Universal Fraud Detection SDK Setup")
    logger.info("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        logger.info("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        logger.info("❌ Failed to create directories")
        sys.exit(1)
    
    # Setup logging
    if not setup_logging():
        logger.info("❌ Failed to setup logging")
        sys.exit(1)
    
    # Create configuration
    if not create_config_file():
        logger.info("❌ Failed to create configuration")
        sys.exit(1)
    
    # Create examples
    if not create_example_scripts():
        logger.info("❌ Failed to create examples")
        sys.exit(1)
    
    # Run tests (optional)
    if os.getenv("SDK_RUN_TESTS", "false").lower() == "true":
        run_tests()
    
    # Print summary
    print_setup_summary()


if __name__ == "__main__":
    main()
