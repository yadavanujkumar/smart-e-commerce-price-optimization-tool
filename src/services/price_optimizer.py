import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
import logging

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


class PriceOptimizer:
    def __init__(self, demand_data, inventory_data, competitor_data, model_type='gradient_boosting'):
        """
        Initializes the PriceOptimizer with necessary data and ML models.

        :param demand_data: DataFrame containing historical demand data.
        :param inventory_data: DataFrame containing inventory levels.
        :param competitor_data: DataFrame containing competitor pricing data.
        :param model_type: Type of ML model to use ('linear', 'random_forest', 'gradient_boosting', 'xgboost', 'lightgbm')
        """
        self.demand_data = demand_data
        self.inventory_data = inventory_data
        self.competitor_data = competitor_data
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.demand_model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the ML model based on model_type."""
        if self.model_type == 'linear':
            self.demand_model = LinearRegression()
        elif self.model_type == 'ridge':
            self.demand_model = Ridge(alpha=1.0)
        elif self.model_type == 'random_forest':
            self.demand_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        elif self.model_type == 'gradient_boosting':
            self.demand_model = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=5)
        elif self.model_type == 'xgboost' and XGBOOST_AVAILABLE:
            self.demand_model = xgb.XGBRegressor(n_estimators=100, random_state=42, max_depth=5)
        elif self.model_type == 'lightgbm' and LIGHTGBM_AVAILABLE:
            self.demand_model = lgb.LGBMRegressor(n_estimators=100, random_state=42, max_depth=5, verbose=-1)
        else:
            # Default to gradient boosting
            self.demand_model = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=5)
    
    def calculate_price_elasticity(self, product_id):
        """
        Calculate price elasticity of demand for a product using economic formula.
        
        :param product_id: ID of the product
        :return: Price elasticity coefficient
        """
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]
        
        if len(product_demand) < 2:
            return -1.0  # Default elasticity
        
        # Calculate elasticity: (% change in quantity) / (% change in price)
        prices = product_demand['price'].values
        quantities = product_demand['quantity'].values
        
        # Use midpoint method for elasticity
        elasticities = []
        for i in range(len(prices) - 1):
            delta_q = quantities[i+1] - quantities[i]
            delta_p = prices[i+1] - prices[i]
            avg_q = (quantities[i+1] + quantities[i]) / 2
            avg_p = (prices[i+1] + prices[i]) / 2
            
            if delta_p != 0 and avg_p != 0:
                elasticity = (delta_q / avg_q) / (delta_p / avg_p)
                elasticities.append(elasticity)
        
        return np.mean(elasticities) if elasticities else -1.0
    
    def calculate_optimal_margin(self, elasticity, base_margin=0.3):
        """
        Calculate optimal profit margin based on price elasticity.
        Uses the inverse elasticity rule: markup = -1 / (elasticity + 1)
        
        :param elasticity: Price elasticity of demand
        :param base_margin: Base profit margin to use as minimum
        :return: Optimal profit margin
        """
        if elasticity >= -1:
            return base_margin
        
        # Inverse elasticity rule
        optimal_margin = -1 / (elasticity + 1)
        
        # Constrain margin between reasonable bounds
        return max(base_margin, min(optimal_margin, 0.8))
    
    def predict_revenue(self, product_id, price):
        """
        Predict revenue at a given price point.
        
        :param product_id: ID of the product
        :param price: Price to evaluate
        :return: Predicted revenue
        """
        predicted_demand = self.simulate_demand(product_id, price)
        return price * predicted_demand

    def optimize_price(self, product_id, min_margin=0.2, max_price_change=0.3):
        """
        Calculates the optimal price for a given product using advanced optimization.

        :param product_id: ID of the product to optimize price for.
        :param min_margin: Minimum profit margin to maintain
        :param max_price_change: Maximum allowed price change (as percentage)
        :return: Optimal price as a float.
        """
        # Extract relevant data for the product
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]
        product_inventory = self.inventory_data[self.inventory_data['product_id'] == product_id]
        product_competitor = self.competitor_data[self.competitor_data['product_id'] == product_id]

        if product_demand.empty or product_inventory.empty or product_competitor.empty:
            raise ValueError(f"Insufficient data for product ID {product_id}")

        # Calculate key metrics
        avg_competitor_price = product_competitor['price'].mean()
        min_competitor_price = product_competitor['price'].min()
        max_competitor_price = product_competitor['price'].max()
        
        # Calculate price elasticity
        elasticity = self.calculate_price_elasticity(product_id)
        
        # Calculate optimal margin based on elasticity
        optimal_margin = self.calculate_optimal_margin(elasticity)

        # Get current price and inventory
        current_price = product_demand['price'].iloc[-1] if len(product_demand) > 0 else avg_competitor_price
        inventory_level = product_inventory['quantity'].iloc[0]
        
        # Dynamic pricing based on inventory levels (urgency-based pricing)
        inventory_adjustment = 1.0
        if inventory_level < 10:  # Very low inventory
            inventory_adjustment = 1.25  # Increase price significantly
        elif inventory_level < 30:  # Low inventory
            inventory_adjustment = 1.10  # Moderate increase
        elif inventory_level > 200:  # Very high inventory
            inventory_adjustment = 0.75  # Aggressive discount
        elif inventory_level > 100:  # High inventory
            inventory_adjustment = 0.90  # Moderate discount

        # Competitive positioning strategy
        competitive_adjustment = 1.0
        price_position = (current_price - min_competitor_price) / (max_competitor_price - min_competitor_price) if max_competitor_price > min_competitor_price else 0.5
        
        # If we're priced too high compared to competitors, adjust down
        if price_position > 0.75:
            competitive_adjustment = 0.95
        # If we're priced too low, we can increase
        elif price_position < 0.25:
            competitive_adjustment = 1.05
        
        # Calculate base optimal price using elasticity-based margin
        base_optimal_price = avg_competitor_price * (1 + optimal_margin)
        
        # Apply all adjustments
        optimal_price = base_optimal_price * inventory_adjustment * competitive_adjustment
        
        # Apply constraints: don't change price too drastically
        max_change_up = current_price * (1 + max_price_change)
        max_change_down = current_price * (1 - max_price_change)
        optimal_price = max(max_change_down, min(max_change_up, optimal_price))
        
        # Ensure we maintain minimum margin
        cost_estimate = avg_competitor_price * (1 - min_margin)  # Rough cost estimate
        min_price = cost_estimate * (1 + min_margin)
        optimal_price = max(min_price, optimal_price)
        
        # Round to psychological pricing (e.g., $9.99 instead of $10.00)
        optimal_price = self._apply_psychological_pricing(optimal_price)
        
        return round(optimal_price, 2)
    
    def _apply_psychological_pricing(self, price):
        """
        Apply psychological pricing strategies (e.g., charm pricing).
        
        :param price: Original price
        :return: Psychologically optimized price
        """
        # For prices over $10, use .99 ending
        if price >= 10:
            return np.floor(price) + 0.99
        # For prices under $10, use .95 ending
        elif price >= 5:
            return np.floor(price) + 0.95
        else:
            return round(price, 2)

    def simulate_demand(self, product_id, price):
        """
        Simulates demand for a given product at a specific price using ML models.

        :param product_id: ID of the product to simulate demand for.
        :param price: Price to simulate demand at.
        :return: Simulated demand as an integer.
        """
        # Extract relevant data for the product
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]

        if product_demand.empty:
            raise ValueError(f"Insufficient demand data for product ID {product_id}")

        # Prepare features for ML model
        X = product_demand[['price']].values
        y = product_demand['quantity'].values
        
        # Train the model if we have enough data
        if len(X) >= 3:
            try:
                self.demand_model.fit(X, y)
                predicted_demand = self.demand_model.predict([[price]])[0]
            except Exception as e:
                # Fallback to linear regression
                logger.warning(f"ML model prediction failed for product {product_id} at price {price}, falling back to linear regression. Error: {e}")
                coef = np.polyfit(product_demand['price'], product_demand['quantity'], 1)
                predicted_demand = coef[0] * price + coef[1]
        else:
            # Use simple linear regression for limited data
            coef = np.polyfit(product_demand['price'], product_demand['quantity'], 1)
            predicted_demand = coef[0] * price + coef[1]

        # Ensure demand is non-negative and reasonable
        predicted_demand = max(int(predicted_demand), 0)
        
        # Add some randomness to simulate market uncertainty (within ±10%)
        uncertainty = np.random.uniform(0.9, 1.1)
        predicted_demand = int(predicted_demand * uncertainty)
        
        return max(predicted_demand, 0)
    
    def find_revenue_maximizing_price(self, product_id, price_range=None, step=1.0):
        """
        Find the price that maximizes revenue for a product.
        
        :param product_id: ID of the product
        :param price_range: Tuple of (min_price, max_price), defaults to ±30% of competitor average
        :param step: Price increment for search
        :return: Dictionary with optimal price, predicted demand, and revenue
        """
        product_competitor = self.competitor_data[self.competitor_data['product_id'] == product_id]
        
        if product_competitor.empty:
            raise ValueError(f"No competitor data for product ID {product_id}")
        
        avg_price = product_competitor['price'].mean()
        
        if price_range is None:
            min_price = avg_price * 0.7
            max_price = avg_price * 1.3
        else:
            min_price, max_price = price_range
        
        best_revenue = 0
        best_price = avg_price
        best_demand = 0
        
        # Search for revenue-maximizing price
        current_price = min_price
        while current_price <= max_price:
            try:
                demand = self.simulate_demand(product_id, current_price)
                revenue = current_price * demand
                
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_price = current_price
                    best_demand = demand
            except Exception as e:
                logger.debug(f"Failed to calculate revenue for product {product_id} at price {current_price:.2f}: {e}")
                pass
            
            current_price += step
        
        return {
            'optimal_price': round(best_price, 2),
            'predicted_demand': best_demand,
            'predicted_revenue': round(best_revenue, 2)
        }
    
    def analyze_competitor_strategy(self, product_id):
        """
        Analyze competitor pricing strategy and positioning.
        
        :param product_id: ID of the product
        :return: Dictionary with competitor analysis
        """
        product_competitor = self.competitor_data[self.competitor_data['product_id'] == product_id]
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]
        
        if product_competitor.empty:
            return {}
        
        prices = product_competitor['price'].values
        
        analysis = {
            'avg_competitor_price': round(prices.mean(), 2),
            'min_competitor_price': round(prices.min(), 2),
            'max_competitor_price': round(prices.max(), 2),
            'price_std_dev': round(prices.std(), 2),
            'price_range': round(prices.max() - prices.min(), 2),
            'num_competitors': len(prices),
        }
        
        if not product_demand.empty:
            our_price = product_demand['price'].iloc[-1]
            analysis['our_current_price'] = round(our_price, 2)
            analysis['price_vs_avg'] = round(((our_price - analysis['avg_competitor_price']) / analysis['avg_competitor_price']) * 100, 2)
            
            if our_price < analysis['min_competitor_price']:
                analysis['position'] = 'price_leader'
            elif our_price > analysis['max_competitor_price']:
                analysis['position'] = 'premium'
            else:
                analysis['position'] = 'competitive'
        
        return analysis


# Example usage
if __name__ == "__main__":
    # Mock data for demonstration purposes
    demand_data = pd.DataFrame({
        'product_id': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        'price': [10, 12, 15, 18, 20, 5, 7, 10, 12, 15],
        'quantity': [120, 110, 80, 65, 60, 220, 200, 150, 130, 100]
    })

    inventory_data = pd.DataFrame({
        'product_id': [1, 2],
        'quantity': [50, 120]
    })

    competitor_data = pd.DataFrame({
        'product_id': [1, 1, 1, 2, 2, 2],
        'price': [12, 14, 13, 6, 8, 7]
    })

    # Test different model types
    print("=" * 80)
    print("Advanced Price Optimization Demo")
    print("=" * 80)
    
    for model_type in ['linear', 'gradient_boosting', 'random_forest']:
        print(f"\n--- Using {model_type.upper().replace('_', ' ')} Model ---")
        optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data, model_type=model_type)

        # Optimize price for product ID 1
        optimal_price = optimizer.optimize_price(1)
        print(f"Optimal price for product ID 1: ${optimal_price}")

        # Calculate elasticity
        elasticity = optimizer.calculate_price_elasticity(1)
        print(f"Price elasticity of demand: {elasticity:.2f}")

        # Simulate demand at optimal price
        simulated_demand = optimizer.simulate_demand(1, optimal_price)
        print(f"Simulated demand at optimal price: {simulated_demand} units")
        
        # Revenue prediction
        revenue = optimizer.predict_revenue(1, optimal_price)
        print(f"Predicted revenue: ${revenue:.2f}")
        
        # Competitor analysis
        comp_analysis = optimizer.analyze_competitor_strategy(1)
        print(f"Competitor analysis: {comp_analysis}")
    
    # Find revenue-maximizing price
    print("\n" + "=" * 80)
    print("Revenue Maximization Analysis")
    print("=" * 80)
    optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data)
    result = optimizer.find_revenue_maximizing_price(1)
    print(f"Revenue-maximizing price: ${result['optimal_price']}")
    print(f"Expected demand: {result['predicted_demand']} units")
    print(f"Expected revenue: ${result['predicted_revenue']}")