import logging
import math
import re
from typing import Any, Dict, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Logging helper
def log_message(level: str, message: str) -> None:
    """
    Logs a message at the specified level.
    
    Args:
        level (str): Logging level ('info', 'warning', 'error', 'debug').
        message (str): Message to log.
    """
    level = level.lower()
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "debug":
        logger.debug(message)
    else:
        raise ValueError(f"Invalid logging level: {level}")

# Data validation helpers
def is_valid_email(email: str) -> bool:
    """
    Validates if the given string is a valid email address.
    
    Args:
        email (str): Email address to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))

def is_positive_number(value: Union[int, float]) -> bool:
    """
    Checks if a number is positive.
    
    Args:
        value (Union[int, float]): Number to check.
    
    Returns:
        bool: True if positive, False otherwise.
    """
    return isinstance(value, (int, float)) and value > 0

def validate_price_data(data: Dict[str, Any]) -> bool:
    """
    Validates price data for the e-commerce optimization tool.
    
    Args:
        data (Dict[str, Any]): Dictionary containing price data.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    required_keys = ["product_id", "price", "currency"]
    for key in required_keys:
        if key not in data:
            log_message("error", f"Missing required key: {key}")
            return False
        if key == "price" and not is_positive_number(data[key]):
            log_message("error", f"Invalid price value: {data[key]}")
            return False
    return True

# Mathematical helpers
def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculates the percentage change between two values.
    
    Args:
        old_value (float): Original value.
        new_value (float): New value.
    
    Returns:
        float: Percentage change.
    """
    if old_value == 0:
        raise ValueError("Old value cannot be zero.")
    return ((new_value - old_value) / old_value) * 100

def calculate_average(values: List[Union[int, float]]) -> float:
    """
    Calculates the average of a list of numbers.
    
    Args:
        values (List[Union[int, float]]): List of numbers.
    
    Returns:
        float: Average value.
    """
    if not values:
        raise ValueError("Values list cannot be empty.")
    return sum(values) / len(values)

def round_to_nearest(value: float, precision: int = 2) -> float:
    """
    Rounds a number to the nearest specified precision.
    
    Args:
        value (float): Number to round.
        precision (int): Decimal places to round to.
    
    Returns:
        float: Rounded number.
    """
    return round(value, precision)

# Example usage of realistic large dataset
def generate_mock_price_data(num_entries: int = 1000) -> List[Dict[str, Any]]:
    """
    Generates a mock dataset of price data for testing.
    
    Args:
        num_entries (int): Number of entries to generate.
    
    Returns:
        List[Dict[str, Any]]: List of mock price data dictionaries.
    """
    import random
    import string

    def random_string(length: int) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    currencies = ["USD", "EUR", "GBP", "JPY", "AUD"]
    data = []
    for _ in range(num_entries):
        product_id = random_string(10)
        price = round(random.uniform(1, 1000), 2)
        currency = random.choice(currencies)
        data.append({"product_id": product_id, "price": price, "currency": currency})
    return data