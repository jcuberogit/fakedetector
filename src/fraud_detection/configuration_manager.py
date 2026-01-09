"""
Configuration management system for the Python Fraud Detection Agent.
Handles loading, validation, and access to configuration settings.
"""

import json
import os
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from pydantic import ValidationError
import logging

from .configuration_models import (
    FraudDetectionAgentConfig,
    DatabaseSettings,
    JwtSettings,
    FraudDetectionSettings,
    AISettings,
    MLModelTrainingSettings,
    DataObservabilitySettings,
    ModelPerformanceMonitoringSettings,
    AdvancedRulesEngineSettings,
    GNNServiceSettings,
    MLDataPipelineSettings,
    DataLineageSettings,
    FeatureVectorSettings,
    MLServiceSettings,
    PredictiveRiskForecastingSettings,
    AzureSettings,
    TimeSeriesBehavioralSettings,
    GPTFineTuningSettings,
    RAGKnowledgeBaseSettings,
    AdvancedAnalyticsSettings,
    ExternalIntegrationSettings,
    ExternalSystemSettings,
    WebhookSubscriptionSettings,
    SerilogSettings,
    ExplainabilityServiceSettings,
    OpenTelemetrySettings,
    JaegerSettings,
    PerformanceSettings
)

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages configuration loading, validation, and access."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default paths.
        """
        self.config_path = config_path
        self._config: Optional[FraudDetectionAgentConfig] = None
        self._raw_config: Dict[str, Any] = {}
        
    def load_config(self, config_path: Optional[str] = None) -> FraudDetectionAgentConfig:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file. If None, uses instance config_path.
            
        Returns:
            Loaded and validated configuration.
            
        Raises:
            FileNotFoundError: If configuration file is not found.
            ValidationError: If configuration validation fails.
        """
        if config_path:
            self.config_path = config_path
            
        if not self.config_path:
            self.config_path = self._find_config_file()
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        # Load raw configuration
        self._raw_config = self._load_raw_config(self.config_path)
        
        # Convert to Pydantic model
        try:
            self._config = FraudDetectionAgentConfig(**self._raw_config)
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self._config
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
            
    def _find_config_file(self) -> str:
        """Find configuration file in common locations."""
        possible_paths = [
            "config.json",
            "appsettings.json",
            "config.yaml",
            "appsettings.yaml",
            "config.yml",
            "appsettings.yml",
            os.path.join("config", "config.json"),
            os.path.join("config", "appsettings.json"),
            os.path.join("config", "config.yaml"),
            os.path.join("config", "appsettings.yaml"),
            os.path.join("config", "config.yml"),
            os.path.join("config", "appsettings.yml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Default to config.json if none found
        return "config.json"
        
    def _load_raw_config(self, config_path: str) -> Dict[str, Any]:
        """Load raw configuration from file."""
        file_ext = Path(config_path).suffix.lower()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if file_ext in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
                
    def get_config(self) -> FraudDetectionAgentConfig:
        """
        Get the loaded configuration.
        
        Returns:
            The loaded configuration.
            
        Raises:
            RuntimeError: If configuration has not been loaded.
        """
        if self._config is None:
            raise RuntimeError("Configuration has not been loaded. Call load_config() first.")
        return self._config
        
    def get_raw_config(self) -> Dict[str, Any]:
        """
        Get the raw configuration dictionary.
        
        Returns:
            The raw configuration dictionary.
        """
        return self._raw_config
        
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get a specific configuration section.
        
        Args:
            section_name: Name of the configuration section.
            
        Returns:
            Configuration section as dictionary.
        """
        config = self.get_config()
        return getattr(config, section_name, {}).dict() if hasattr(config, section_name) else {}
        
    def get_setting(self, section_name: str, setting_name: str, default: Any = None) -> Any:
        """
        Get a specific setting from a configuration section.
        
        Args:
            section_name: Name of the configuration section.
            setting_name: Name of the setting.
            default: Default value if setting is not found.
            
        Returns:
            The setting value or default.
        """
        section = self.get_section(section_name)
        return section.get(setting_name, default)
        
    def update_setting(self, section_name: str, setting_name: str, value: Any) -> None:
        """
        Update a specific setting in the configuration.
        
        Args:
            section_name: Name of the configuration section.
            setting_name: Name of the setting.
            value: New value for the setting.
        """
        if self._config is None:
            raise RuntimeError("Configuration has not been loaded. Call load_config() first.")
            
        # Update the raw config
        if section_name not in self._raw_config:
            self._raw_config[section_name] = {}
        self._raw_config[section_name][setting_name] = value
        
        # Reload the configuration to validate
        try:
            self._config = FraudDetectionAgentConfig(**self._raw_config)
            logger.info(f"Updated setting {section_name}.{setting_name} = {value}")
        except ValidationError as e:
            logger.error(f"Configuration update validation failed: {e}")
            raise
            
    def save_config(self, config_path: Optional[str] = None) -> None:
        """
        Save the current configuration to file.
        
        Args:
            config_path: Path to save configuration. If None, uses current config_path.
        """
        if config_path:
            self.config_path = config_path
            
        if not self.config_path:
            raise ValueError("No configuration path specified")
            
        file_ext = Path(self.config_path).suffix.lower()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            if file_ext in ['.yaml', '.yml']:
                yaml.dump(self._raw_config, f, default_flow_style=False, indent=2)
            else:
                json.dump(self._raw_config, f, indent=2)
                
        logger.info(f"Configuration saved to {self.config_path}")
        
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        try:
            if self._config is None:
                return False
            # Pydantic model validation is already done during loading
            return True
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
            
    def get_database_config(self) -> DatabaseSettings:
        """Get database configuration."""
        return self.get_config().database
        
    def get_jwt_config(self) -> JwtSettings:
        """Get JWT configuration."""
        return self.get_config().jwt_settings
        
    def get_fraud_detection_config(self) -> FraudDetectionSettings:
        """Get fraud detection configuration."""
        return self.get_config().fraud_detection
        
    def get_ai_config(self) -> AISettings:
        """Get AI configuration."""
        return self.get_config().ai
        
    def get_ml_model_training_config(self) -> MLModelTrainingSettings:
        """Get ML model training configuration."""
        return self.get_config().ml_model_training
        
    def get_data_observability_config(self) -> DataObservabilitySettings:
        """Get data observability configuration."""
        return self.get_config().data_observability
        
    def get_model_performance_monitoring_config(self) -> ModelPerformanceMonitoringSettings:
        """Get model performance monitoring configuration."""
        return self.get_config().model_performance_monitoring
        
    def get_advanced_rules_engine_config(self) -> AdvancedRulesEngineSettings:
        """Get advanced rules engine configuration."""
        return self.get_config().advanced_rules_engine
        
    def get_gnn_service_config(self) -> GNNServiceSettings:
        """Get GNN service configuration."""
        return self.get_config().gnn_service
        
    def get_ml_data_pipeline_config(self) -> MLDataPipelineSettings:
        """Get ML data pipeline configuration."""
        return self.get_config().ml_data_pipeline
        
    def get_data_lineage_config(self) -> DataLineageSettings:
        """Get data lineage configuration."""
        return self.get_config().data_lineage
        
    def get_feature_vector_config(self) -> FeatureVectorSettings:
        """Get feature vector configuration."""
        return self.get_config().feature_vector
        
    def get_ml_service_config(self) -> MLServiceSettings:
        """Get ML service configuration."""
        return self.get_config().ml_service
        
    def get_predictive_risk_forecasting_config(self) -> PredictiveRiskForecastingSettings:
        """Get predictive risk forecasting configuration."""
        return self.get_config().predictive_risk_forecasting
        
    def get_azure_config(self) -> AzureSettings:
        """Get Azure configuration."""
        return self.get_config().azure
        
    def get_time_series_behavioral_config(self) -> TimeSeriesBehavioralSettings:
        """Get time series behavioral configuration."""
        return self.get_config().time_series_behavioral
        
    def get_gpt_fine_tuning_config(self) -> GPTFineTuningSettings:
        """Get GPT fine-tuning configuration."""
        return self.get_config().gpt_fine_tuning
        
    def get_rag_knowledge_base_config(self) -> RAGKnowledgeBaseSettings:
        """Get RAG knowledge base configuration."""
        return self.get_config().rag_knowledge_base
        
    def get_advanced_analytics_config(self) -> AdvancedAnalyticsSettings:
        """Get advanced analytics configuration."""
        return self.get_config().advanced_analytics
        
    def get_external_integration_config(self) -> ExternalIntegrationSettings:
        """Get external integration configuration."""
        return self.get_config().external_integration
        
    def get_external_systems_config(self) -> Dict[str, ExternalSystemSettings]:
        """Get external systems configuration."""
        return self.get_config().external_systems
        
    def get_webhook_subscriptions_config(self) -> Dict[str, WebhookSubscriptionSettings]:
        """Get webhook subscriptions configuration."""
        return self.get_config().webhook_subscriptions
        
    def get_serilog_config(self) -> SerilogSettings:
        """Get Serilog configuration."""
        return self.get_config().serilog
        
    def get_explainability_service_config(self) -> ExplainabilityServiceSettings:
        """Get explainability service configuration."""
        return self.get_config().explainability_service
        
    def get_open_telemetry_config(self) -> OpenTelemetrySettings:
        """Get OpenTelemetry configuration."""
        return self.get_config().open_telemetry
        
    def get_jaeger_config(self) -> JaegerSettings:
        """Get Jaeger configuration."""
        return self.get_config().jaeger
        
    def get_performance_config(self) -> PerformanceSettings:
        """Get performance configuration."""
        return self.get_config().performance


class ConfigurationLoader:
    """Utility class for loading configuration from various sources."""
    
    @staticmethod
    def load_from_file(file_path: str) -> FraudDetectionAgentConfig:
        """
        Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file.
            
        Returns:
            Loaded configuration.
        """
        manager = ConfigurationManager(file_path)
        return manager.load_config()
        
    @staticmethod
    def load_from_dict(config_dict: Dict[str, Any]) -> FraudDetectionAgentConfig:
        """
        Load configuration from a dictionary.
        
        Args:
            config_dict: Configuration dictionary.
            
        Returns:
            Loaded configuration.
        """
        try:
            return FraudDetectionAgentConfig(**config_dict)
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
            
    @staticmethod
    def load_from_env() -> FraudDetectionAgentConfig:
        """
        Load configuration from environment variables.
        
        Returns:
            Loaded configuration.
        """
        config_dict = {}
        
        # Map environment variables to configuration keys
        env_mappings = {
            'FRAUD_DETECTION_HIGH_RISK_THRESHOLD': ('fraud_detection', 'high_risk_threshold'),
            'FRAUD_DETECTION_CRITICAL_RISK_THRESHOLD': ('fraud_detection', 'critical_risk_threshold'),
            'JWT_SECRET_KEY': ('jwt_settings', 'secret_key'),
            'JWT_ISSUER': ('jwt_settings', 'issuer'),
            'JWT_AUDIENCE': ('jwt_settings', 'audience'),
            'JWT_EXPIRY_MINUTES': ('jwt_settings', 'expiry_minutes'),
            'AI_TEMPERATURE': ('ai', 'temperature'),
            'AI_MAX_TOKENS': ('ai', 'max_tokens'),
            'OPENAI_API_KEY': ('openai', 'api_key'),
            'OPENAI_MODEL': ('openai', 'model'),
            'DATABASE_PROVIDER': ('database', 'provider'),
            'REDIS_CONNECTION_STRING': ('connection_strings', 'redis'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in config_dict:
                    config_dict[section] = {}
                    
                # Convert string values to appropriate types
                if key in ['high_risk_threshold', 'critical_risk_threshold', 'temperature']:
                    config_dict[section][key] = float(value)
                elif key in ['max_tokens', 'expiry_minutes']:
                    config_dict[section][key] = int(value)
                else:
                    config_dict[section][key] = value
                    
        return ConfigurationLoader.load_from_dict(config_dict)
        
    @staticmethod
    def create_default_config() -> FraudDetectionAgentConfig:
        """
        Create a default configuration.
        
        Returns:
            Default configuration.
        """
        return FraudDetectionAgentConfig()


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        The global configuration manager.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_config(config_path: Optional[str] = None) -> FraudDetectionAgentConfig:
    """
    Load configuration using the global configuration manager.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Loaded configuration.
    """
    manager = get_config_manager()
    return manager.load_config(config_path)


def get_config() -> FraudDetectionAgentConfig:
    """
    Get the loaded configuration.
    
    Returns:
        The loaded configuration.
    """
    return get_config_manager().get_config()
