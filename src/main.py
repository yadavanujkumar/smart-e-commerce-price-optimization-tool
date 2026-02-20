import logging
import os
import sys
import pandas as pd
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from services.price_optimizer import PriceOptimizer
from repositories.data_repository import DataRepository
from models.product import Product

def setup_logging():
    """Sets up logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized with level: %s", log_level)

def main():
    """Main entry point for the application."""
    setup_logging()
    logging.info("Starting Smart E-Commerce Price Optimization Tool...")

    # Initialize configuration
    config = Config()
    logging.info("Configuration loaded: %s", config.get("APP_NAME"))

    # Initialize data repository
    db_path = config.get("DATABASE_URL", "sqlite:///data/smart_ecommerce.db").replace("sqlite:///", "")
    repo = DataRepository(db_path=db_path)
    
    # Add mock data if database is empty
    products = repo.get_product_data()
    if not products:
        logging.info("No products found. Adding mock data...")
        repo.add_mock_data()
        products = repo.get_product_data()
    
    logging.info("Loaded %d products from database", len(products))
    
    # Create sample data for price optimizer
    demand_data = pd.DataFrame({
        'product_id': [p['id'] for p in products for _ in range(3)],
        'price': [p['price'] * m for p in products for m in [0.8, 1.0, 1.2]],
        'quantity': [int(p['stock'] * m) for p in products for m in [1.5, 1.0, 0.7]]
    })
    
    inventory_data = pd.DataFrame({
        'product_id': [p['id'] for p in products],
        'quantity': [p['stock'] for p in products]
    })
    
    # Get competitor data for each product
    competitor_data_list = []
    for product in products:
        comp_data = repo.fetch_competitor_data(product['id'])
        for comp in comp_data:
            competitor_data_list.append({
                'product_id': product['id'],
                'price': comp['competitor_price']
            })
    
    if competitor_data_list:
        competitor_data = pd.DataFrame(competitor_data_list)
    else:
        # Create mock competitor data
        competitor_data = pd.DataFrame({
            'product_id': [p['id'] for p in products for _ in range(2)],
            'price': [p['price'] * m for p in products for m in [0.95, 1.05]]
        })
    
    # Initialize price optimizer
    optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data)
    
    # Optimize prices for all products
    logging.info("Optimizing prices for %d products...", len(products))
    for product in products[:5]:  # Optimize first 5 products as example
        try:
            optimal_price = optimizer.optimize_price(product['id'])
            repo.save_optimized_prices(product['id'], optimal_price)
            logging.info("Product '%s' (ID: %d): Current price $%.2f -> Optimal price $%.2f", 
                        product['name'], product['id'], product['price'], optimal_price)
            
            # Simulate demand at optimal price
            simulated_demand = optimizer.simulate_demand(product['id'], optimal_price)
            logging.info("  Simulated demand at optimal price: %d units", simulated_demand)
        except Exception as e:
            logging.error("Failed to optimize price for product %d: %s", product['id'], e)
    
    logging.info("Price optimization completed successfully!")

if __name__ == "__main__":
    main()