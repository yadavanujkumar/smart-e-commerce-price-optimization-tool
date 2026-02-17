#!/usr/bin/env python3
"""
Example usage script demonstrating the enhanced Smart E-Commerce Price Optimization Tool.
This script shows how to:
1. Load and initialize the price optimizer
2. Optimize prices for products
3. Analyze competitor strategies
4. Generate visualizations
5. Use the ML models for predictions
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.services.price_optimizer import PriceOptimizer
from src.repositories.data_repository import DataRepository
from src.models.product import Product
from src.config import Config
from src.utils.visualizations import (
    plot_price_demand_curve,
    plot_revenue_optimization,
    plot_competitor_comparison,
    create_dashboard_summary
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for data generation
DEMAND_PRICE_MULTIPLIERS = [0.7, 0.85, 1.0, 1.15, 1.3]
DEMAND_QUANTITY_MULTIPLIERS = [2.0, 1.5, 1.0, 0.7, 0.5]
COMPETITOR_PRICE_MULTIPLIERS = [0.9, 1.0, 1.1]


def main():
    """Main demonstration function."""
    
    print("=" * 80)
    print("Smart E-Commerce Price Optimization Tool - Enhanced Demo")
    print("=" * 80)
    print()
    
    # Initialize configuration
    config = Config()
    logger.info(f"Application: {config.get('APP_NAME')} v{config.get('VERSION')}")
    
    # Initialize data repository
    db_path = "data/smart_ecommerce.db"
    repo = DataRepository(db_path=db_path)
    
    # Load products
    products = repo.get_product_data()
    if not products:
        logger.info("No products found. Adding mock data...")
        repo.add_mock_data()
        products = repo.get_product_data()
    
    logger.info(f"Loaded {len(products)} products")
    
    # Prepare data for optimizer
    demand_data = pd.DataFrame({
        'product_id': [p['id'] for p in products for _ in range(len(DEMAND_PRICE_MULTIPLIERS))],
        'price': [p['price'] * m for p in products for m in DEMAND_PRICE_MULTIPLIERS],
        'quantity': [int(p['stock'] * m) for p in products for m in DEMAND_QUANTITY_MULTIPLIERS]
    })
    
    inventory_data = pd.DataFrame({
        'product_id': [p['id'] for p in products],
        'quantity': [p['stock'] for p in products]
    })
    
    # Get competitor data
    competitor_data_list = []
    for product in products:
        comp_data = repo.fetch_competitor_data(product['id'])
        for comp in comp_data:
            competitor_data_list.append({
                'product_id': product['id'],
                'price': comp['competitor_price']
            })
    
    competitor_data = pd.DataFrame(competitor_data_list) if competitor_data_list else pd.DataFrame({
        'product_id': [p['id'] for p in products for _ in range(len(COMPETITOR_PRICE_MULTIPLIERS))],
        'price': [p['price'] * m for p in products for m in COMPETITOR_PRICE_MULTIPLIERS]
    })
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 1: Advanced Price Optimization")
    print("=" * 80)
    
    # Initialize optimizer with different models
    models_to_test = ['linear', 'gradient_boosting', 'random_forest']
    
    for model_type in models_to_test:
        print(f"\n--- Testing {model_type.upper().replace('_', ' ')} Model ---")
        
        optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data, model_type=model_type)
        
        # Test on first product
        product = products[0]
        product_id = product['id']
        
        try:
            # Calculate optimal price
            optimal_price = optimizer.optimize_price(product_id)
            
            # Calculate elasticity
            elasticity = optimizer.calculate_price_elasticity(product_id)
            
            # Simulate demand
            simulated_demand = optimizer.simulate_demand(product_id, optimal_price)
            
            # Predict revenue
            predicted_revenue = optimizer.predict_revenue(product_id, optimal_price)
            
            print(f"Product: {product['name']} (ID: {product_id})")
            print(f"  Current Price: ${product['price']:.2f}")
            print(f"  Optimal Price: ${optimal_price:.2f}")
            print(f"  Price Change: ${optimal_price - product['price']:.2f} ({((optimal_price - product['price']) / product['price']) * 100:.1f}%)")
            print(f"  Price Elasticity: {elasticity:.2f}")
            print(f"  Predicted Demand: {simulated_demand} units")
            print(f"  Predicted Revenue: ${predicted_revenue:.2f}")
            
        except Exception as e:
            logger.error(f"Error optimizing product {product_id}: {e}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 2: Revenue Maximization")
    print("=" * 80)
    
    optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data)
    
    for i, product in enumerate(products[:3]):  # Test first 3 products
        try:
            result = optimizer.find_revenue_maximizing_price(product['id'])
            print(f"\n{i+1}. {product['name']}")
            print(f"   Current Price: ${product['price']:.2f}")
            print(f"   Revenue-Maximizing Price: ${result['optimal_price']:.2f}")
            print(f"   Expected Demand: {result['predicted_demand']} units")
            print(f"   Expected Revenue: ${result['predicted_revenue']:.2f}")
        except Exception as e:
            logger.error(f"Error analyzing product {product['id']}: {e}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 3: Competitor Analysis")
    print("=" * 80)
    
    for i, product in enumerate(products[:3]):
        try:
            analysis = optimizer.analyze_competitor_strategy(product['id'])
            print(f"\n{i+1}. {product['name']} - Competitor Analysis:")
            print(f"   Number of Competitors: {analysis.get('num_competitors', 0)}")
            print(f"   Average Competitor Price: ${analysis.get('avg_competitor_price', 0):.2f}")
            print(f"   Price Range: ${analysis.get('price_range', 0):.2f}")
            print(f"   Our Position: {analysis.get('position', 'Unknown')}")
            if 'price_vs_avg' in analysis:
                print(f"   Price vs Average: {analysis['price_vs_avg']:.1f}%")
        except Exception as e:
            logger.error(f"Error analyzing competitors for product {product['id']}: {e}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 4: Enhanced Product Model")
    print("=" * 80)
    
    # Create Product instances with enhanced features
    test_product = Product(
        product_id="TEST-001",
        name="Premium Wireless Headphones",
        price=199.99,
        demand=150,
        inventory=75,
        cost=120.00,
        category="Electronics"
    )
    
    print(f"\nProduct: {test_product.name}")
    print(f"  Price: ${test_product.price:.2f}")
    print(f"  Cost: ${test_product.cost:.2f}")
    print(f"  Profit Margin: {test_product.calculate_profit_margin():.1f}%")
    print(f"  Markup: {test_product.calculate_markup():.1f}%")
    print(f"  Revenue: ${test_product.calculate_revenue():.2f}")
    print(f"  Profit: ${test_product.calculate_profit():.2f}")
    print(f"  Inventory Value: ${test_product.calculate_inventory_value():.2f}")
    print(f"  Stock Status: {test_product.get_stock_status()}")
    print(f"  Is Profitable: {test_product.is_profitable()}")
    
    # Test price update with history
    print("\n  Testing price updates:")
    test_product.update_price(189.99)
    print(f"  New Price: ${test_product.price:.2f}")
    print(f"  Price History Entries: {len(test_product.get_price_history())}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 5: Visualization Generation")
    print("=" * 80)
    
    try:
        # Generate visualizations
        product = products[0]
        product_id = product['id']
        
        print(f"\nGenerating visualizations for {product['name']}...")
        
        # Price-demand curve
        fig1 = plot_price_demand_curve(demand_data, product_id, product['name'])
        fig1.write_html('/tmp/price_demand_curve.html')
        print("  ✓ Price-demand curve saved to /tmp/price_demand_curve.html")
        
        # Revenue optimization
        fig2 = plot_revenue_optimization(product_id, optimizer, product['name'])
        fig2.write_html('/tmp/revenue_optimization.html')
        print("  ✓ Revenue optimization chart saved to /tmp/revenue_optimization.html")
        
        # Competitor comparison
        fig3 = plot_competitor_comparison(competitor_data, product_id, product['price'], product['name'])
        fig3.write_html('/tmp/competitor_comparison.html')
        print("  ✓ Competitor comparison saved to /tmp/competitor_comparison.html")
        
        # Dashboard summary
        optimized_prices = {p['id']: optimizer.optimize_price(p['id']) for p in products[:5]}
        fig4 = create_dashboard_summary(products, optimized_prices)
        fig4.write_html('/tmp/dashboard_summary.html')
        print("  ✓ Dashboard summary saved to /tmp/dashboard_summary.html")
        
        print("\n  All visualizations generated successfully!")
        print("  Open the HTML files in a web browser to view interactive charts.")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION 6: Batch Price Optimization")
    print("=" * 80)
    
    print("\nOptimizing prices for all products...\n")
    
    optimized_results = []
    for product in products:
        try:
            optimal_price = optimizer.optimize_price(product['id'])
            revenue = optimizer.predict_revenue(product['id'], optimal_price)
            
            optimized_results.append({
                'name': product['name'],
                'current_price': product['price'],
                'optimal_price': optimal_price,
                'change': optimal_price - product['price'],
                'change_pct': ((optimal_price - product['price']) / product['price']) * 100,
                'predicted_revenue': revenue
            })
        except Exception as e:
            logger.error(f"Error optimizing {product['name']}: {e}")
    
    # Display results sorted by expected revenue gain
    optimized_results.sort(key=lambda x: x['predicted_revenue'], reverse=True)
    
    print(f"{'Product':<25} {'Current':<10} {'Optimal':<10} {'Change':<12} {'Revenue':<12}")
    print("-" * 80)
    
    for result in optimized_results:
        print(f"{result['name']:<25} "
              f"${result['current_price']:<9.2f} "
              f"${result['optimal_price']:<9.2f} "
              f"{result['change_pct']:>6.1f}% "
              f"${result['predicted_revenue']:>11.2f}")
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Multiple ML models (Linear, Random Forest, Gradient Boosting)")
    print("  ✓ Price elasticity calculation using economic formulas")
    print("  ✓ Revenue maximization algorithms")
    print("  ✓ Competitor strategy analysis")
    print("  ✓ Enhanced product model with cost and margin tracking")
    print("  ✓ Interactive visualizations with Plotly")
    print("  ✓ Batch optimization for multiple products")
    print("\nFor API usage, run: python src/api.py")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)
