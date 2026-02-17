import logging
import os
import json
from optimization_service import PriceOptimizationService
from config_loader import ConfigLoader

def setup_logging():
    """Sets up logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized with level: %s", log_level)

def load_configuration():
    """Loads the application configuration."""
    config_path = os.getenv("CONFIG_PATH", "config.json")
    if not os.path.exists(config_path):
        logging.error("Configuration file not found at %s", config_path)
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, "r") as config_file:
        try:
            config = json.load(config_file)
            logging.info("Configuration loaded successfully.")
            return config
        except json.JSONDecodeError as e:
            logging.error("Failed to parse configuration file: %s", e)
            raise

def main():
    """Main entry point for the application."""
    setup_logging()
    logging.info("Starting Smart E-Commerce Price Optimization Tool...")

    try:
        config = load_configuration()
    except Exception as e:
        logging.critical("Failed to load configuration: %s", e)
        return

    try:
        optimization_service = PriceOptimizationService(config)
        optimization_service.start()
        logging.info("Price Optimization Service started successfully.")
    except Exception as e:
        logging.critical("Failed to start Price Optimization Service: %s", e)

if __name__ == "__main__":
    main()