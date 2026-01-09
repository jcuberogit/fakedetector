#!/usr/bin/env python3
"""
Centralized Client Configuration Manager
========================================

This module provides a centralized way for all ParadigmStore agents to access
client-specific configuration data (business details, branding, localization, etc.)

Usage:
    from shared.client_config_manager import get_client_config, ClientConfigManager
    
    # Get specific client config
    config = get_client_config("hello-store-001")
    
    # Access specific data
    brand_name = config.get_brand_name()
    whatsapp_phone = config.get_whatsapp_phone()
    language = config.get_language()
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ClientConfig:
    """
    Wrapper class for client configuration with convenient access methods
    """
    
    def __init__(self, client_id: str, config_data: Dict[str, Any]):
        self.client_id = client_id
        self._config = config_data
    
    # Business Info
    def get_client_name(self) -> str:
        return self._config.get("client_info", {}).get("client_name", "Unknown Store")
    
    def get_company_name(self) -> str:
        """Get the legal company name"""
        return self._config.get("client_info", {}).get("company_name") or \
               self._config.get("branding", {}).get("company_name") or \
               self.get_client_name()
    
    def get_company_id(self) -> str:
        """Get the legal company ID (Cédula Jurídica for Costa Rica)"""
        return self._config.get("client_info", {}).get("company_id", "")
    
    def get_brand_name(self) -> str:
        # Brand name is the customer-facing name (Hello Store)
        # Return store_name or client_name as the customer-facing brand
        return self._config.get("branding", {}).get("store_name") or \
               self.get_client_name()
    
    def get_business_type(self) -> str:
        return self._config.get("client_info", {}).get("business_type", "retail")
    
    def get_domain(self) -> str:
        return self._config.get("client_info", {}).get("domain", "")
    
    def get_contact_email(self) -> str:
        return self._config.get("client_info", {}).get("contact_email", "")
    
    # Localization
    def get_language(self) -> str:
        return self._config.get("localization", {}).get("language", "en")
    
    def get_country(self) -> str:
        return self._config.get("localization", {}).get("country", "US")
    
    def get_currency(self) -> str:
        return self._config.get("localization", {}).get("currency", "USD")
    
    def get_timezone(self) -> str:
        return self._config.get("localization", {}).get("timezone", "UTC")
    
    # Branding
    def get_store_name(self) -> str:
        return self._config.get("branding", {}).get("store_name", self.get_client_name())
    
    def get_primary_color(self) -> str:
        return self._config.get("branding", {}).get("primary_color", "#007BFF")
    
    def get_secondary_color(self) -> str:
        return self._config.get("branding", {}).get("secondary_color", "#6C757D")
    
    def get_logo_url(self) -> Optional[str]:
        return self._config.get("branding", {}).get("logo_url")
    
    def get_whatsapp_sticker_id(self) -> Optional[str]:
        return self._config.get("branding", {}).get("whatsapp_sticker_id")
    
    def get_welcome_sticker_id(self) -> Optional[str]:
        return self._config.get("branding", {}).get("welcome_sticker_id") or \
               self.get_whatsapp_sticker_id()
    
    def get_logo_base64(self) -> Optional[str]:
        return self._config.get("branding", {}).get("logo_base64")
    
    def should_show_logo_in_messages(self) -> bool:
        return self._config.get("branding", {}).get("display_preferences", {}).get("show_logo_in_messages", True)
    
    def should_show_sticker_in_welcome(self) -> bool:
        return self._config.get("branding", {}).get("display_preferences", {}).get("show_sticker_in_welcome", True)
    
    def should_show_company_in_footer(self) -> bool:
        return self._config.get("branding", {}).get("display_preferences", {}).get("show_company_name_in_footer", True)
    
    def get_logo_size(self) -> str:
        return self._config.get("branding", {}).get("display_preferences", {}).get("logo_size", "80px")
    
    # WhatsApp Integration
    def get_whatsapp_phone(self) -> str:
        whatsapp_config = self._config.get("whatsapp_integration", {})
        return whatsapp_config.get("current_phone") or \
               whatsapp_config.get("sandbox_phone") or \
               whatsapp_config.get("production_phone", "")
    
    def get_whatsapp_environment(self) -> str:
        return self._config.get("whatsapp_integration", {}).get("environment", "production")
    
    def get_whatsapp_webhook_url(self) -> str:
        return self._config.get("whatsapp_integration", {}).get("webhook_url", "")
    
    def get_catalog_url(self) -> str:
        return self._config.get("whatsapp_integration", {}).get("catalog_url", "")
    
    def get_test_phone_number(self) -> str:
        return self._config.get("whatsapp_integration", {}).get("test_phone_number", "")
    
    # Payment Methods
    def get_payment_methods(self) -> Dict[str, Any]:
        return self._config.get("payment_methods", {})
    
    def get_preferred_payment_method(self) -> str:
        agent_config = self._config.get("agent_configuration", {})
        return agent_config.get("payment_processing", {}).get("preferred_method", "credit_card")
    
    # Agent Configuration
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get agent-specific configuration"""
        agent_configs = self._config.get("agent_configuration", {})
        
        # Map agent names to config keys
        agent_key_map = {
            "paradigm.customer-service.agent": "customer_service",
            "paradigm.product-catalog.agent": "product_catalog", 
            "paradigm.payment.agent": "payment_processing",
            "paradigm.marketing.agent": "marketing",
            "paradigm.fraud.agent": "fraud_detection"
        }
        
        config_key = agent_key_map.get(agent_name, agent_name.replace("paradigm.", "").replace(".agent", ""))
        return agent_configs.get(config_key, {})
    
    # Business Settings
    def get_business_hours(self) -> Dict[str, Any]:
        return self._config.get("business_settings", {}).get("business_hours", {})
    
    def get_tax_rate(self) -> float:
        return self._config.get("business_settings", {}).get("tax_rate", 0.0)
    
    def get_shipping_zones(self) -> list:
        return self._config.get("business_settings", {}).get("shipping_zones", [])
    
    # Security Settings
    def get_allowed_domains(self) -> list:
        return self._config.get("security_settings", {}).get("allowed_domains", [])
    
    def get_api_rate_limits(self) -> Dict[str, str]:
        return self._config.get("security_settings", {}).get("api_rate_limits", {})
    
    # Helper Methods
    def is_spanish_speaking(self) -> bool:
        return self.get_language().lower() in ['es', 'español', 'spanish']
    
    def is_costa_rican(self) -> bool:
        return self.get_country().upper() == 'CR'
    
    def is_sandbox_environment(self) -> bool:
        return self.get_whatsapp_environment().lower() == 'sandbox'
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary"""
        return self._config


class ClientConfigManager:
    """
    Manages loading and caching of client configurations
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Auto-detect ParadigmStore root
            current_path = Path(__file__).parent.parent
            self.base_path = current_path / "clients"
        else:
            self.base_path = Path(base_path)
        
        self._config_cache = {}
        logger.info(f"📁 ClientConfigManager initialized with base path: {self.base_path}")
    
    def get_client_config(self, client_id: str) -> Optional[ClientConfig]:
        """
        Load client configuration by client ID
        
        Args:
            client_id: The client identifier (e.g., 'hello-store-001')
            
        Returns:
            ClientConfig object or None if not found
        """
        
        # Check cache first
        if client_id in self._config_cache:
            return self._config_cache[client_id]
        
        # Try different client directory naming patterns
        possible_dirs = [
            client_id,
            client_id.replace('-001', ''),  # hello-store-001 -> hello-store
            client_id.replace('-', '_'),    # hello-store -> hello_store
        ]
        
        for dir_name in possible_dirs:
            config_path = self.base_path / dir_name / "config" / "client_config.json"
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    client_config = ClientConfig(client_id, config_data)
                    self._config_cache[client_id] = client_config
                    
                    logger.info(f"✅ Loaded config for {client_id} from {config_path}")
                    return client_config
                    
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logger.error(f"❌ Error loading config for {client_id}: {e}")
                    continue
        
        logger.warning(f"⚠️ No configuration found for client: {client_id}")
        return None
    
    def list_available_clients(self) -> list:
        """List all available client configurations"""
        clients = []
        
        if not self.base_path.exists():
            return clients
        
        for client_dir in self.base_path.iterdir():
            if client_dir.is_dir() and client_dir.name != "shared-config":
                config_file = client_dir / "config" / "client_config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                        client_id = config_data.get("client_info", {}).get("client_id", client_dir.name)
                        clients.append({
                            "client_id": client_id,
                            "directory": client_dir.name,
                            "name": config_data.get("client_info", {}).get("client_name", "Unknown"),
                            "domain": config_data.get("client_info", {}).get("domain", ""),
                            "status": config_data.get("client_info", {}).get("status", "unknown")
                        })
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        logger.warning(f"⚠️ Error reading config for {client_dir.name}: {e}")
        
        return clients
    
    def clear_cache(self):
        """Clear the configuration cache"""
        self._config_cache.clear()
        logger.info("🧹 Client configuration cache cleared")


# Global instance for easy access
_config_manager = ClientConfigManager()

def get_client_config(client_id: str) -> Optional[ClientConfig]:
    """
    Convenience function to get client configuration
    
    Args:
        client_id: The client identifier
        
    Returns:
        ClientConfig object or None if not found
    """
    return _config_manager.get_client_config(client_id)

def list_clients() -> list:
    """
    Convenience function to list all available clients
    
    Returns:
        List of client information dictionaries
    """
    return _config_manager.list_available_clients()

def clear_config_cache():
    """Clear the configuration cache"""
    _config_manager.clear_cache()


# Example usage and testing
if __name__ == "__main__":
    # Test the configuration manager
    logger.info("🧪 Testing Client Configuration Manager")
    logger.info("=" * 50)
    
    # List available clients
    clients = list_clients()
    logger.info(f"Available clients: {len(clients)}")
    for client in clients:
        logger.info(f"  - {client['client_id']}: {client['name']} ({client['domain']})")
    
    # Test Hello Store configuration
    hello_store = get_client_config("hello-store-001")
    if hello_store:
        logger.info(f"\n📱 Hello Store Configuration:")
        logger.info(f"  Business Name: {hello_store.get_client_name()}")
        logger.info(f"  Company Name: {hello_store.get_company_name()}")
        logger.info(f"  Company ID (Cédula Jurídica): {hello_store.get_company_id()}")
        logger.info(f"  Brand Name: {hello_store.get_brand_name()}")
        logger.info(f"  Language: {hello_store.get_language()}")
        logger.info(f"  Country: {hello_store.get_country()}")
        logger.info(f"  Currency: {hello_store.get_currency()}")
        logger.info(f"  WhatsApp Phone: {hello_store.get_whatsapp_phone()}")
        logger.info(f"  Environment: {hello_store.get_whatsapp_environment()}")
        logger.info(f"  Domain: {hello_store.get_domain()}")
        logger.info(f"\n🎨 Branding & Display:")
        logger.info(f"  Primary Color: {hello_store.get_primary_color()}")
        logger.info(f"  Logo URL: {hello_store.get_logo_url()}")
        logger.info(f"  WhatsApp Sticker ID: {hello_store.get_whatsapp_sticker_id()}")
        logger.info(f"  Welcome Sticker ID: {hello_store.get_welcome_sticker_id()}")
        logger.info(f"  Show Logo in Messages: {hello_store.should_show_logo_in_messages()}")
        logger.info(f"  Show Sticker in Welcome: {hello_store.should_show_sticker_in_welcome()}")
        logger.info(f"  Show Company in Footer: {hello_store.should_show_company_in_footer()}")
        logger.info(f"  Logo Size: {hello_store.get_logo_size()}")
        logger.info(f"\n🌍 Localization:")
        logger.info(f"  Is Spanish Speaking: {hello_store.is_spanish_speaking()}")
        logger.info(f"  Is Costa Rican: {hello_store.is_costa_rican()}")
        logger.info(f"  Is Sandbox: {hello_store.is_sandbox_environment()}")
    else:
        logger.info("❌ Hello Store configuration not found")
