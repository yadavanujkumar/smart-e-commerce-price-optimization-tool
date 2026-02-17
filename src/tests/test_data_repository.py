import pytest
from unittest.mock import MagicMock, patch
from src.data_repository import DataRepository

# Mock data for testing
mock_data = [
    {"product_id": 1, "price": 19.99, "stock": 100, "category": "electronics"},
    {"product_id": 2, "price": 5.49, "stock": 200, "category": "stationery"},
    {"product_id": 3, "price": 299.99, "stock": 50, "category": "appliances"},
    {"product_id": 4, "price": 15.99, "stock": 150, "category": "books"},
    {"product_id": 5, "price": 49.99, "stock": 75, "category": "fashion"},
]

@pytest.fixture
def data_repository():
    """Fixture to create a DataRepository instance."""
    return DataRepository()

@patch("src.data_repository.DatabaseConnection")
def test_get_all_products(mock_db_connection, data_repository):
    """Test retrieving all products from the repository."""
    # Mock database connection and query
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_data
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Call the method
    result = data_repository.get_all_products()

    # Assertions
    assert len(result) == len(mock_data)
    assert result == mock_data
    mock_cursor.execute.assert_called_once_with("SELECT * FROM products")

@patch("src.data_repository.DatabaseConnection")
def test_get_product_by_id(mock_db_connection, data_repository):
    """Test retrieving a product by its ID."""
    product_id = 3
    expected_product = mock_data[2]

    # Mock database connection and query
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = expected_product
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Call the method
    result = data_repository.get_product_by_id(product_id)

    # Assertions
    assert result == expected_product
    mock_cursor.execute.assert_called_once_with("SELECT * FROM products WHERE product_id = %s", (product_id,))

@patch("src.data_repository.DatabaseConnection")
def test_add_product(mock_db_connection, data_repository):
    """Test adding a new product to the repository."""
    new_product = {"product_id": 6, "price": 25.99, "stock": 120, "category": "toys"}

    # Mock database connection
    mock_cursor = MagicMock()
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Call the method
    data_repository.add_product(new_product)

    # Assertions
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO products (product_id, price, stock, category) VALUES (%s, %s, %s, %s)",
        (new_product["product_id"], new_product["price"], new_product["stock"], new_product["category"]),
    )

@patch("src.data_repository.DatabaseConnection")
def test_update_product(mock_db_connection, data_repository):
    """Test updating an existing product in the repository."""
    product_id = 2
    updated_data = {"price": 6.99, "stock": 180}

    # Mock database connection
    mock_cursor = MagicMock()
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Call the method
    data_repository.update_product(product_id, updated_data)

    # Assertions
    mock_cursor.execute.assert_called_once_with(
        "UPDATE products SET price = %s, stock = %s WHERE product_id = %s",
        (updated_data["price"], updated_data["stock"], product_id),
    )

@patch("src.data_repository.DatabaseConnection")
def test_delete_product(mock_db_connection, data_repository):
    """Test deleting a product from the repository."""
    product_id = 4

    # Mock database connection
    mock_cursor = MagicMock()
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

    # Call the method
    data_repository.delete_product(product_id)

    # Assertions
    mock_cursor.execute.assert_called_once_with("DELETE FROM products WHERE product_id = %s", (product_id,))