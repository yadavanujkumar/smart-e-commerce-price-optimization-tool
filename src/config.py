import os
import json
from pathlib import Path

class Config:
    """
    Centralized configuration management for the Smart E-Commerce Price Optimization Tool.
    Loads environment variables, default settings, and external configuration files.
    Provides access to application settings.
    """

    def __init__(self, config_file_path=None):
        """
        Initialize the Config class.
        :param config_file_path: Optional path to an external configuration file.
        """
        self._config = {}
        self._load_defaults()
        self._load_environment_variables()
        if config_file_path:
            self._load_external_config(config_file_path)

    def _load_defaults(self):
        """
        Load default settings into the configuration.
        """
        self._config.update({
            "APP_NAME": "Smart E-Commerce Price Optimization Tool",
            "VERSION": "2.0",
            "DEBUG": False,
            "LOG_LEVEL": "INFO",
            "DATABASE_URL": "sqlite:///data/db.sqlite3",
            "CACHE_TIMEOUT": 300,  # seconds
            "API_RATE_LIMIT": 1000,  # requests per minute
            "SUPPORTED_CURRENCIES": ["USD", "EUR", "GBP", "JPY"],
            "DEFAULT_CURRENCY": "USD",
            "MAX_PRODUCTS": 100000,  # maximum number of products supported
            
            # Machine Learning Configuration
            "PRICE_OPTIMIZATION_ALGORITHM": "gradient_boosting",
            "ML_MODEL_OPTIONS": ["linear", "ridge", "random_forest", "gradient_boosting", "xgboost", "lightgbm"],
            "DEFAULT_ML_MODEL": "gradient_boosting",
            "ML_N_ESTIMATORS": 100,
            "ML_MAX_DEPTH": 5,
            "ML_RANDOM_STATE": 42,
            
            # Price Optimization Parameters
            "MIN_PROFIT_MARGIN": 0.20,  # 20% minimum margin
            "MAX_PRICE_CHANGE": 0.30,  # Maximum 30% price change
            "ENABLE_PSYCHOLOGICAL_PRICING": True,
            "PSYCHOLOGICAL_PRICE_ENDINGS": [0.99, 0.95, 0.89],
            
            # Inventory Thresholds
            "VERY_LOW_INVENTORY_THRESHOLD": 10,
            "LOW_INVENTORY_THRESHOLD": 30,
            "HIGH_INVENTORY_THRESHOLD": 100,
            "VERY_HIGH_INVENTORY_THRESHOLD": 200,
            
            # Pricing Adjustments
            "VERY_LOW_INVENTORY_MULTIPLIER": 1.25,
            "LOW_INVENTORY_MULTIPLIER": 1.10,
            "HIGH_INVENTORY_MULTIPLIER": 0.90,
            "VERY_HIGH_INVENTORY_MULTIPLIER": 0.75,
            
            # Revenue Optimization
            "REVENUE_SEARCH_STEP": 1.0,  # Price increment for revenue search
            "REVENUE_PRICE_RANGE_MIN": 0.7,  # 70% of competitor average
            "REVENUE_PRICE_RANGE_MAX": 1.3,  # 130% of competitor average
            
            # API Configuration
            "API_HOST": "0.0.0.0",
            "API_PORT": 5000,
            "API_DEBUG": False,
            "ENABLE_CORS": True,
            
            # Feature Flags
            "ENABLE_ML_MODELS": True,
            "ENABLE_ELASTICITY_CALCULATION": True,
            "ENABLE_COMPETITOR_ANALYSIS": True,
            "ENABLE_VISUALIZATION": True,
        })

    def _load_environment_variables(self):
        """
        Load environment variables into the configuration.
        """
        for key in self._config.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert environment variables to appropriate types
                if env_value.isdigit():
                    env_value = int(env_value)
                elif env_value.lower() in ["true", "false"]:
                    env_value = env_value.lower() == "true"
                self._config[key] = env_value

    def _load_external_config(self, config_file_path):
        """
        Load external configuration file into the configuration.
        :param config_file_path: Path to the external configuration file.
        """
        config_path = Path(config_file_path)
        if config_path.is_file():
            with open(config_path, "r") as file:
                external_config = json.load(file)
                self._config.update(external_config)

    def get(self, key, default=None):
        """
        Get a configuration value by key.
        :param key: Configuration key.
        :param default: Default value if the key is not found.
        :return: Configuration value.
        """
        return self._config.get(key, default)

    def set(self, key, value):
        """
        Set a configuration value by key.
        :param key: Configuration key.
        :param value: Value to set.
        """
        self._config[key] = value

    def all(self):
        """
        Get all configuration values.
        :return: Dictionary of all configuration values.
        """
        return self._config


# Example usage:
# config = Config(config_file_path="config.json")
# print(config.get("APP_NAME"))
# print(config.all())