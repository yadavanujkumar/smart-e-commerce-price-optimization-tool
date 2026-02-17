# Changelog

All notable changes to the Smart E-Commerce Price Optimization Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-17

### Added - Major Enhancement Release

#### Core Features
- **Advanced ML Models**: Integrated 6 machine learning models
  - Linear Regression (baseline)
  - Ridge Regression (regularized)
  - Random Forest (ensemble learning)
  - Gradient Boosting (high accuracy, default)
  - XGBoost (optional, industry-standard)
  - LightGBM (optional, fast and efficient)
- **Price Elasticity Calculation**: Economic formula-based elasticity using midpoint method
- **Revenue Maximization**: Algorithm to find price point that maximizes revenue
- **Psychological Pricing**: Automatic charm pricing with .99/.95 endings
- **Competitor Analysis**: Comprehensive competitive positioning and price gap analysis
- **Enhanced Product Model**: Cost tracking, profit margins, markup calculations, inventory valuation
- **Price History Tracking**: Maintains history of all price changes with timestamps

#### API & Integration
- **Flask REST API**: Production-ready API with 10+ endpoints
  - `/optimize/price` - Optimize product pricing
  - `/predict/demand` - Predict demand at price point
  - `/predict/revenue` - Revenue forecasting
  - `/analyze/competitor/<id>` - Competitor strategy analysis
  - `/optimize/revenue` - Find revenue-maximizing price
  - Plus product CRUD operations
- **JSON Responses**: Standardized API responses with error handling
- **Comprehensive Error Handling**: Detailed error messages and HTTP status codes

#### Visualization
- **Interactive Charts**: Plotly-powered visualizations
  - Price-demand curves with trend lines
  - Revenue optimization plots
  - Competitor comparison bar charts
  - Price elasticity distribution
  - Inventory vs price scatter plots
  - Profit margin analysis
  - Dashboard summary with KPIs
- **Export Capabilities**: Save visualizations as HTML, PNG, PDF, SVG

#### Analytics & Optimization
- **Optimal Margin Calculation**: Uses inverse elasticity rule
- **Inventory-Aware Pricing**: 4-tier threshold system with dynamic adjustments
- **Competitive Positioning**: Automatic classification (price leader/competitive/premium)
- **Demand Simulation**: ML-based demand prediction with uncertainty modeling
- **Batch Optimization**: Process multiple products efficiently

#### Configuration
- **Enhanced Config System**: 40+ configurable parameters
  - ML model selection and hyperparameters
  - Pricing constraints and thresholds
  - Inventory level definitions
  - Pricing adjustment multipliers
  - API settings
  - Feature flags
- **Environment Variable Support**: Override any config via env vars

#### Documentation & Examples
- **Comprehensive README**: 500+ lines with detailed documentation
- **Example Usage Script**: `example_usage.py` demonstrating all features
- **API Documentation**: Complete endpoint documentation with examples
- **Code Examples**: Python SDK usage, visualization generation, model usage
- **Performance Metrics**: Benchmarks and scalability information

### Changed

#### Improvements
- **main.py**: Fixed to use existing modules instead of non-existent imports
  - Removed references to `optimization_service` and `config_loader`
  - Integrated with actual repository and optimizer classes
  - Added proper data initialization and mock data handling
  - Enhanced logging with detailed price optimization results
- **PriceOptimizer**: Complete rewrite with advanced algorithms
  - Multi-model support with model selection
  - Economic-based elasticity calculation
  - Revenue maximization search algorithm
  - Psychological pricing application
  - Constraint-based optimization (margins, max price change)
  - Competitive positioning analysis
- **Product Model**: Enhanced from basic to advanced analytics
  - Added cost tracking (constructor parameter)
  - Added category support
  - Profit margin and markup calculations
  - Inventory valuation methods
  - Stock status classification
  - Price history with timestamps
  - Enhanced validation (price > cost)
- **Config**: Expanded from 8 to 40+ configuration parameters
  - ML model configuration
  - Pricing strategy parameters
  - Inventory thresholds
  - API settings
  - Feature flags

### Fixed
- **Import Errors**: Corrected all module import paths in main.py
- **Syntax Errors**: Fixed list comprehensions in data preparation
- **Database Path**: Ensured data directory creation before DB operations
- **Model Fallbacks**: Graceful fallback to Gradient Boosting if optional packages missing

### Technical Details
- **Lines of Code**: Increased from ~500 to 2000+ lines
- **API Endpoints**: 0 → 10 endpoints
- **ML Models**: 1 → 6 models
- **Visualization Functions**: 0 → 8 functions
- **Configuration Parameters**: 8 → 40+ parameters
- **Test Coverage**: Enhanced test infrastructure
- **Documentation**: README expanded from 46 to 500+ lines

### Dependencies
- Maintained all existing dependencies
- Added optional dependencies (xgboost, lightgbm) with fallback support
- No breaking changes to existing dependencies

## [1.0.0] - Previous Release

### Initial Release
- Basic price optimization using simple linear correlation
- SQLite database with product, competitor, and optimization tables
- Basic Product model
- Simple configuration system
- Basic helper utilities
- Initial test infrastructure
- Docker support
- Basic README

---

## Migration Guide (1.0 → 2.0)

### Breaking Changes
**None** - Version 2.0 is fully backward compatible

### Recommended Updates

1. **Update imports** (if using old main.py):
   ```python
   # Old
   from optimization_service import PriceOptimizationService
   
   # New
   from services.price_optimizer import PriceOptimizer
   ```

2. **Use enhanced Product model**:
   ```python
   # Old
   product = Product(id, name, price, demand, inventory)
   
   # New - with cost tracking
   product = Product(id, name, price, demand, inventory, cost=price*0.6, category="Electronics")
   ```

3. **Leverage new ML models**:
   ```python
   # Old - only basic linear
   optimizer = PriceOptimizer(demand, inventory, competitor)
   
   # New - choose your model
   optimizer = PriceOptimizer(demand, inventory, competitor, model_type='gradient_boosting')
   ```

4. **Use new API endpoints**:
   - Start API server: `python src/api.py`
   - Access at `http://localhost:5000`
   - See README for endpoint documentation

5. **Generate visualizations**:
   ```python
   from src.utils.visualizations import plot_revenue_optimization
   fig = plot_revenue_optimization(product_id, optimizer)
   fig.write_html('output.html')
   ```

### Deprecated
- None in this release

### Removed
- None in this release
