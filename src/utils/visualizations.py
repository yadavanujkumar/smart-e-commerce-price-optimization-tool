"""
Visualization utilities for price optimization analysis.
Uses Plotly for interactive charts and graphs.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any


def plot_price_demand_curve(demand_data: pd.DataFrame, product_id: int, product_name: str = "Product"):
    """
    Plot the price-demand curve for a product.
    
    :param demand_data: DataFrame with price and quantity columns
    :param product_id: Product ID to filter data
    :param product_name: Name of the product for the title
    :return: Plotly figure object
    """
    product_data = demand_data[demand_data['product_id'] == product_id].sort_values('price')
    
    fig = go.Figure()
    
    # Add scatter plot for actual data points
    fig.add_trace(go.Scatter(
        x=product_data['price'],
        y=product_data['quantity'],
        mode='markers',
        name='Historical Data',
        marker=dict(size=10, color='blue')
    ))
    
    # Add trend line
    if len(product_data) >= 2:
        z = np.polyfit(product_data['price'], product_data['quantity'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(product_data['price'].min(), product_data['price'].max(), 100)
        y_trend = p(x_trend)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode='lines',
            name='Trend Line',
            line=dict(color='red', dash='dash')
        ))
    
    fig.update_layout(
        title=f'Price-Demand Curve: {product_name}',
        xaxis_title='Price ($)',
        yaxis_title='Demand (units)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_revenue_optimization(product_id: int, optimizer, product_name: str = "Product"):
    """
    Plot revenue across different price points to visualize optimal price.
    
    :param product_id: Product ID
    :param optimizer: PriceOptimizer instance
    :param product_name: Name of the product
    :return: Plotly figure object
    """
    # Get competitor average price
    competitor_data = optimizer.competitor_data[optimizer.competitor_data['product_id'] == product_id]
    avg_comp_price = competitor_data['price'].mean()
    
    # Generate price range
    prices = np.linspace(avg_comp_price * 0.5, avg_comp_price * 1.5, 50)
    revenues = []
    demands = []
    
    for price in prices:
        try:
            demand = optimizer.simulate_demand(product_id, price)
            revenue = price * demand
            revenues.append(revenue)
            demands.append(demand)
        except:
            revenues.append(0)
            demands.append(0)
    
    # Create subplot with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Revenue vs Price', 'Demand vs Price'),
        vertical_spacing=0.15
    )
    
    # Revenue plot
    fig.add_trace(
        go.Scatter(x=prices, y=revenues, mode='lines', name='Revenue',
                  line=dict(color='green', width=2)),
        row=1, col=1
    )
    
    # Find max revenue point
    max_revenue_idx = np.argmax(revenues)
    fig.add_trace(
        go.Scatter(x=[prices[max_revenue_idx]], y=[revenues[max_revenue_idx]],
                  mode='markers', name='Max Revenue',
                  marker=dict(size=12, color='red', symbol='star')),
        row=1, col=1
    )
    
    # Demand plot
    fig.add_trace(
        go.Scatter(x=prices, y=demands, mode='lines', name='Demand',
                  line=dict(color='blue', width=2)),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Price ($)", row=2, col=1)
    fig.update_yaxes(title_text="Revenue ($)", row=1, col=1)
    fig.update_yaxes(title_text="Demand (units)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        title_text=f"Revenue Optimization Analysis: {product_name}",
        showlegend=True,
        template='plotly_white'
    )
    
    return fig


def plot_competitor_comparison(competitor_data: pd.DataFrame, product_id: int, 
                               our_price: float, product_name: str = "Product"):
    """
    Plot competitor price comparison.
    
    :param competitor_data: DataFrame with competitor pricing
    :param product_id: Product ID
    :param our_price: Our current price
    :param product_name: Product name
    :return: Plotly figure object
    """
    product_comp = competitor_data[competitor_data['product_id'] == product_id]
    
    # Add our price to the data
    all_prices = list(product_comp['price'].values) + [our_price]
    labels = [f'Competitor {i+1}' for i in range(len(product_comp))] + ['Our Price']
    colors = ['lightblue'] * len(product_comp) + ['orange']
    
    fig = go.Figure(data=[
        go.Bar(x=labels, y=all_prices, marker_color=colors)
    ])
    
    # Add average line
    avg_comp_price = product_comp['price'].mean()
    fig.add_hline(y=avg_comp_price, line_dash="dash", line_color="red",
                  annotation_text=f"Avg: ${avg_comp_price:.2f}")
    
    fig.update_layout(
        title=f'Competitor Price Comparison: {product_name}',
        xaxis_title='',
        yaxis_title='Price ($)',
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def plot_price_elasticity_distribution(elasticities: Dict[int, float], product_names: Dict[int, str]):
    """
    Plot distribution of price elasticities across products.
    
    :param elasticities: Dictionary mapping product_id to elasticity
    :param product_names: Dictionary mapping product_id to product name
    :return: Plotly figure object
    """
    product_ids = list(elasticities.keys())
    elasticity_values = list(elasticities.values())
    names = [product_names.get(pid, f"Product {pid}") for pid in product_ids]
    
    # Color code by elasticity (elastic vs inelastic)
    colors = ['green' if e < -1 else 'orange' if e < 0 else 'red' for e in elasticity_values]
    
    fig = go.Figure(data=[
        go.Bar(x=names, y=elasticity_values, marker_color=colors)
    ])
    
    # Add reference lines
    fig.add_hline(y=-1, line_dash="dash", line_color="black",
                  annotation_text="Unitary Elastic")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title='Price Elasticity Distribution Across Products',
        xaxis_title='Product',
        yaxis_title='Price Elasticity',
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def plot_inventory_price_matrix(products: List[Dict[str, Any]]):
    """
    Create a scatter plot showing inventory levels vs prices.
    
    :param products: List of product dictionaries
    :return: Plotly figure object
    """
    df = pd.DataFrame(products)
    
    fig = px.scatter(df, x='price', y='stock', 
                     size='stock', color='category',
                     hover_data=['name'],
                     title='Inventory vs Price Analysis',
                     labels={'price': 'Price ($)', 'stock': 'Stock Level'})
    
    fig.update_layout(template='plotly_white')
    
    return fig


def plot_profit_margin_analysis(products: List[Dict[str, Any]], costs: Dict[int, float]):
    """
    Visualize profit margins across products.
    
    :param products: List of product dictionaries
    :param costs: Dictionary mapping product_id to cost
    :return: Plotly figure object
    """
    product_names = [p['name'] for p in products]
    prices = [p['price'] for p in products]
    product_costs = [costs.get(p['id'], p['price'] * 0.6) for p in products]
    margins = [((p - c) / p) * 100 if p > 0 else 0 
               for p, c in zip(prices, product_costs)]
    
    fig = go.Figure()
    
    # Stacked bar chart showing cost and margin
    fig.add_trace(go.Bar(
        name='Cost',
        x=product_names,
        y=product_costs,
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        name='Profit',
        x=product_names,
        y=[p - c for p, c in zip(prices, product_costs)],
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Cost and Profit Breakdown by Product',
        xaxis_title='Product',
        yaxis_title='Amount ($)',
        template='plotly_white'
    )
    
    return fig


def create_dashboard_summary(products: List[Dict[str, Any]], 
                            optimized_prices: Dict[int, float]):
    """
    Create a summary dashboard with key metrics.
    
    :param products: List of product dictionaries
    :param optimized_prices: Dictionary mapping product_id to optimized price
    :return: Plotly figure object
    """
    # Calculate metrics
    total_products = len(products)
    avg_current_price = np.mean([p['price'] for p in products])
    avg_optimized_price = np.mean([optimized_prices.get(p['id'], p['price']) 
                                   for p in products])
    avg_price_change = ((avg_optimized_price - avg_current_price) / avg_current_price) * 100
    
    # Create figure with 4 indicator plots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=("Total Products", "Avg Current Price", 
                       "Avg Optimized Price", "Avg Price Change")
    )
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_products,
        title={"text": "Total Products"},
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=avg_current_price,
        title={"text": "Avg Current Price"},
        number={'prefix': "$", 'valueformat': ".2f"}
    ), row=1, col=2)
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=avg_optimized_price,
        delta={'reference': avg_current_price, 'relative': False},
        title={"text": "Avg Optimized Price"},
        number={'prefix': "$", 'valueformat': ".2f"}
    ), row=2, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=avg_price_change,
        title={"text": "Avg Price Change"},
        number={'suffix': "%", 'valueformat': ".2f"}
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="Price Optimization Dashboard Summary",
        height=600,
        template='plotly_white'
    )
    
    return fig


def save_plot(fig, filename: str, format: str = 'html'):
    """
    Save a plotly figure to file.
    
    :param fig: Plotly figure object
    :param filename: Output filename
    :param format: Output format ('html', 'png', 'pdf', 'svg')
    """
    if format == 'html':
        fig.write_html(filename)
    else:
        fig.write_image(filename)
