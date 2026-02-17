import sqlite3
import json
from typing import List, Dict, Any


class DataRepository:
    def __init__(self, db_path: str = "data/smart_ecommerce.db"):
        """
        Initializes the DataRepository with a connection to the SQLite database.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """
        Ensures the database and required tables exist.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """)

        # Create optimized_prices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimized_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            optimized_price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)

        # Create competitor_data table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            competitor_name TEXT NOT NULL,
            competitor_price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)

        connection.commit()
        connection.close()

    def get_product_data(self) -> List[Dict[str, Any]]:
        """
        Retrieves all product data from the database.
        :return: List of dictionaries containing product data.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, category, price, stock FROM products")
        rows = cursor.fetchall()

        connection.close()

        return [
            {"id": row[0], "name": row[1], "category": row[2], "price": row[3], "stock": row[4]}
            for row in rows
        ]

    def save_optimized_prices(self, product_id: int, optimized_price: float) -> None:
        """
        Saves optimized price for a product into the database.
        :param product_id: ID of the product.
        :param optimized_price: Optimized price to save.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO optimized_prices (product_id, optimized_price)
        VALUES (?, ?)
        """, (product_id, optimized_price))

        connection.commit()
        connection.close()

    def fetch_competitor_data(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Fetches competitor data for a specific product.
        :param product_id: ID of the product.
        :return: List of dictionaries containing competitor data.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT competitor_name, competitor_price, timestamp
        FROM competitor_data
        WHERE product_id = ?
        """, (product_id,))
        rows = cursor.fetchall()

        connection.close()

        return [
            {"competitor_name": row[0], "competitor_price": row[1], "timestamp": row[2]}
            for row in rows
        ]

    def add_mock_data(self) -> None:
        """
        Adds mock data to the database for testing purposes.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Insert mock products
        products = [
            ("Laptop", "Electronics", 999.99, 50),
            ("Smartphone", "Electronics", 699.99, 100),
            ("Headphones", "Accessories", 199.99, 200),
            ("Desk Chair", "Furniture", 149.99, 30),
            ("Gaming Console", "Electronics", 499.99, 20)
        ]
        cursor.executemany("""
        INSERT INTO products (name, category, price, stock)
        VALUES (?, ?, ?, ?)
        """, products)

        # Insert mock competitor data
        competitor_data = [
            (1, "Competitor A", 950.00),
            (1, "Competitor B", 980.00),
            (2, "Competitor A", 680.00),
            (2, "Competitor B", 710.00),
            (3, "Competitor A", 190.00),
            (3, "Competitor B", 200.00),
            (4, "Competitor A", 140.00),
            (4, "Competitor B", 150.00),
            (5, "Competitor A", 480.00),
            (5, "Competitor B", 500.00)
        ]
        cursor.executemany("""
        INSERT INTO competitor_data (product_id, competitor_name, competitor_price)
        VALUES (?, ?, ?)
        """, competitor_data)

        connection.commit()
        connection.close()