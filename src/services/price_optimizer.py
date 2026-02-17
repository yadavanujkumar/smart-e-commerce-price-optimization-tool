import numpy as np
import pandas as pd

class PriceOptimizer:
    def __init__(self, demand_data, inventory_data, competitor_data):
        """
        Initializes the PriceOptimizer with necessary data.

        :param demand_data: DataFrame containing historical demand data.
        :param inventory_data: DataFrame containing inventory levels.
        :param competitor_data: DataFrame containing competitor pricing data.
        """
        self.demand_data = demand_data
        self.inventory_data = inventory_data
        self.competitor_data = competitor_data

    def optimize_price(self, product_id):
        """
        Calculates the optimal price for a given product based on demand, inventory, and competitor data.

        :param product_id: ID of the product to optimize price for.
        :return: Optimal price as a float.
        """
        # Extract relevant data for the product
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]
        product_inventory = self.inventory_data[self.inventory_data['product_id'] == product_id]
        product_competitor = self.competitor_data[self.competitor_data['product_id'] == product_id]

        if product_demand.empty or product_inventory.empty or product_competitor.empty:
            raise ValueError(f"Insufficient data for product ID {product_id}")

        # Calculate average competitor price
        avg_competitor_price = product_competitor['price'].mean()

        # Calculate demand elasticity (simplified formula)
        demand_elasticity = np.corrcoef(product_demand['price'], product_demand['quantity'])[0, 1]

        # Adjust price based on inventory levels
        inventory_level = product_inventory['quantity'].iloc[0]
        if inventory_level < 10:  # Low inventory
            price_adjustment = 1.2  # Increase price
        elif inventory_level > 100:  # High inventory
            price_adjustment = 0.8  # Decrease price
        else:
            price_adjustment = 1.0  # No adjustment

        # Calculate optimal price
        optimal_price = avg_competitor_price * (1 + demand_elasticity) * price_adjustment
        return round(optimal_price, 2)

    def simulate_demand(self, product_id, price):
        """
        Simulates demand for a given product at a specific price.

        :param product_id: ID of the product to simulate demand for.
        :param price: Price to simulate demand at.
        :return: Simulated demand as an integer.
        """
        # Extract relevant data for the product
        product_demand = self.demand_data[self.demand_data['product_id'] == product_id]

        if product_demand.empty:
            raise ValueError(f"Insufficient demand data for product ID {product_id}")

        # Fit a simple linear regression model to predict demand
        X = product_demand['price'].values.reshape(-1, 1)
        y = product_demand['quantity'].values

        # Use numpy for linear regression (simplified)
        coef = np.polyfit(product_demand['price'], product_demand['quantity'], 1)
        predicted_demand = coef[0] * price + coef[1]

        # Ensure demand is non-negative
        return max(int(predicted_demand), 0)


# Example usage
if __name__ == "__main__":
    # Mock data for demonstration purposes
    demand_data = pd.DataFrame({
        'product_id': [1, 1, 1, 2, 2, 2],
        'price': [10, 15, 20, 5, 10, 15],
        'quantity': [100, 80, 60, 200, 150, 100]
    })

    inventory_data = pd.DataFrame({
        'product_id': [1, 2],
        'quantity': [50, 120]
    })

    competitor_data = pd.DataFrame({
        'product_id': [1, 1, 2, 2],
        'price': [12, 14, 6, 8]
    })

    optimizer = PriceOptimizer(demand_data, inventory_data, competitor_data)

    # Optimize price for product ID 1
    optimal_price = optimizer.optimize_price(1)
    print(f"Optimal price for product ID 1: ${optimal_price}")

    # Simulate demand for product ID 1 at price $18
    simulated_demand = optimizer.simulate_demand(1, 18)
    print(f"Simulated demand for product ID 1 at $18: {simulated_demand}")