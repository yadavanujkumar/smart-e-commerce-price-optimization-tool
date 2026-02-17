"""
Flask API for Smart E-Commerce Price Optimization Tool
Provides REST endpoints for price optimization, analysis, and predictions.
"""

from flask import Flask, request, jsonify
import pandas as pd
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.price_optimizer import PriceOptimizer
from repositories.data_repository import DataRepository
from models.product import Product
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for data (in production, use proper database connection)
config = Config()
db_path = config.get("DATABASE_URL", "sqlite:///data/smart_ecommerce.db").replace("sqlite:///", "")
repository = DataRepository(db_path=db_path)


def load_optimizer_data():
    """Load data from repository and create optimizer instance."""
    products = repository.get_product_data()
    
    if not products:
        repository.add_mock_data()
        products = repository.get_product_data()
    
    # Create sample demand data
    demand_data = pd.DataFrame({
        'product_id': [p['id'] for p in products for _ in range(3)],
        'price': [p['price'] * 0.8, p['price'], p['price'] * 1.2 for p in products],
        'quantity': [int(p['stock'] * 1.5), p['stock'], int(p['stock'] * 0.7) for p in products]
    })
    
    inventory_data = pd.DataFrame({
        'product_id': [p['id'] for p in products],
        'quantity': [p['stock'] for p in products]
    })
    
    # Get competitor data
    competitor_data_list = []
    for product in products:
        comp_data = repository.fetch_competitor_data(product['id'])
        for comp in comp_data:
            competitor_data_list.append({
                'product_id': product['id'],
                'price': comp['competitor_price']
            })
    
    if competitor_data_list:
        competitor_data = pd.DataFrame(competitor_data_list)
    else:
        competitor_data = pd.DataFrame({
            'product_id': [p['id'] for p in products for _ in range(2)],
            'price': [p['price'] * 0.95, p['price'] * 1.05 for p in products]
        })
    
    return PriceOptimizer(demand_data, inventory_data, competitor_data), products


@app.route('/')
def home():
    """API home endpoint."""
    return jsonify({
        'name': 'Smart E-Commerce Price Optimization API',
        'version': '2.0',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /products': 'List all products',
            'GET /products/<id>': 'Get product details',
            'POST /optimize/price': 'Optimize price for a product',
            'POST /predict/demand': 'Predict demand at a price point',
            'POST /predict/revenue': 'Predict revenue at a price point',
            'GET /analyze/competitor/<id>': 'Analyze competitor pricing',
            'POST /optimize/revenue': 'Find revenue-maximizing price',
        }
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200


@app.route('/products', methods=['GET'])
def get_products():
    """Get all products."""
    try:
        products = repository.get_product_data()
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        }), 200
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product."""
    try:
        products = repository.get_product_data()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        return jsonify({'success': True, 'product': product}), 200
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/optimize/price', methods=['POST'])
def optimize_price():
    """
    Optimize price for a product.
    Request body: {"product_id": 1, "model_type": "gradient_boosting"}
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        model_type = data.get('model_type', 'gradient_boosting')
        
        if not product_id:
            return jsonify({'success': False, 'error': 'product_id is required'}), 400
        
        optimizer, products = load_optimizer_data()
        optimizer.model_type = model_type
        optimizer._initialize_model()
        
        product = next((p for p in products if p['id'] == product_id), None)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        optimal_price = optimizer.optimize_price(product_id)
        elasticity = optimizer.calculate_price_elasticity(product_id)
        simulated_demand = optimizer.simulate_demand(product_id, optimal_price)
        predicted_revenue = optimal_price * simulated_demand
        
        # Save to database
        repository.save_optimized_prices(product_id, optimal_price)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product['name'],
            'current_price': product['price'],
            'optimal_price': optimal_price,
            'price_change': round(optimal_price - product['price'], 2),
            'price_change_percent': round(((optimal_price - product['price']) / product['price']) * 100, 2),
            'price_elasticity': round(elasticity, 2),
            'predicted_demand': simulated_demand,
            'predicted_revenue': round(predicted_revenue, 2),
            'model_used': model_type
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error optimizing price: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict/demand', methods=['POST'])
def predict_demand():
    """
    Predict demand at a specific price point.
    Request body: {"product_id": 1, "price": 15.99}
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        price = data.get('price')
        
        if not product_id or price is None:
            return jsonify({'success': False, 'error': 'product_id and price are required'}), 400
        
        optimizer, products = load_optimizer_data()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        predicted_demand = optimizer.simulate_demand(product_id, price)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product['name'],
            'price': price,
            'predicted_demand': predicted_demand
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error predicting demand: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict/revenue', methods=['POST'])
def predict_revenue():
    """
    Predict revenue at a specific price point.
    Request body: {"product_id": 1, "price": 15.99}
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        price = data.get('price')
        
        if not product_id or price is None:
            return jsonify({'success': False, 'error': 'product_id and price are required'}), 400
        
        optimizer, products = load_optimizer_data()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        predicted_revenue = optimizer.predict_revenue(product_id, price)
        predicted_demand = optimizer.simulate_demand(product_id, price)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product['name'],
            'price': price,
            'predicted_demand': predicted_demand,
            'predicted_revenue': round(predicted_revenue, 2)
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error predicting revenue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analyze/competitor/<int:product_id>', methods=['GET'])
def analyze_competitor(product_id):
    """Analyze competitor pricing strategy for a product."""
    try:
        optimizer, products = load_optimizer_data()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        analysis = optimizer.analyze_competitor_strategy(product_id)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product['name'],
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing competitor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/optimize/revenue', methods=['POST'])
def optimize_revenue():
    """
    Find the price that maximizes revenue.
    Request body: {"product_id": 1, "min_price": 10, "max_price": 30, "step": 0.5}
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        step = data.get('step', 1.0)
        
        if not product_id:
            return jsonify({'success': False, 'error': 'product_id is required'}), 400
        
        optimizer, products = load_optimizer_data()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        price_range = (min_price, max_price) if min_price and max_price else None
        result = optimizer.find_revenue_maximizing_price(product_id, price_range, step)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product['name'],
            'current_price': product['price'],
            'revenue_maximizing_price': result['optimal_price'],
            'predicted_demand': result['predicted_demand'],
            'predicted_revenue': result['predicted_revenue']
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error optimizing revenue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize database with mock data if empty
    products = repository.get_product_data()
    if not products:
        logger.info("Initializing database with mock data...")
        repository.add_mock_data()
    
    logger.info("Starting Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
