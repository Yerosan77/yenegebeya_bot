"""
In-memory data storage for the bot.
In a production environment, this should be replaced with a proper database.
"""

import logging

logger = logging.getLogger(__name__)

# Categories storage
categories = []

# Products storage
products = []

# Shopping cart storage (user_id -> list of product_ids)
cart = {}

# Order history storage (for future use)
orders = {}

# Pending payments storage (order_id -> order_details)
pending_payments = {}

# Order counter for unique order IDs
order_counter = 1000

def initialize_sample_data():
    """Initialize with some sample data for testing purposes."""
    global categories, products
    
    # Add sample categories
    sample_categories = ["Electronics", "Clothing", "Books", "Home & Garden"]
    categories.extend(sample_categories)
    
    # Add sample products
    sample_products = [
        {
            "id": 1,
            "name": "Smartphone",
            "price": 15000,
            "description": "Latest Android smartphone with great features",
            "image": "https://via.placeholder.com/300x300?text=Smartphone",
            "category": "Electronics",
            "stock": 10
        },
        {
            "id": 2,
            "name": "T-Shirt",
            "price": 500,
            "description": "Comfortable cotton t-shirt in various colors",
            "image": "https://via.placeholder.com/300x300?text=T-Shirt",
            "category": "Clothing",
            "stock": 25
        },
        {
            "id": 3,
            "name": "Novel Book",
            "price": 300,
            "description": "Bestselling fiction novel in Amharic",
            "image": "https://via.placeholder.com/300x300?text=Book",
            "category": "Books",
            "stock": 15
        }
    ]
    
    products.extend(sample_products)
    logger.info("Sample data initialized")

def get_user_cart(user_id: int) -> list:
    """Get user's cart items."""
    return cart.get(user_id, [])

def add_to_user_cart(user_id: int, product_id: int):
    """Add product to user's cart."""
    if user_id not in cart:
        cart[user_id] = []
    cart[user_id].append(product_id)

def clear_user_cart(user_id: int):
    """Clear user's cart."""
    cart[user_id] = []

def get_product_by_id(product_id: int):
    """Get product by ID."""
    return next((p for p in products if p['id'] == product_id), None)

def get_products_by_category(category: str):
    """Get all products in a category."""
    return [p for p in products if p['category'].lower() == category.lower()]

def category_exists(category: str) -> bool:
    """Check if category exists."""
    return any(cat.lower() == category.lower() for cat in categories)

# Initialize sample data when module is imported
# Comment out the following line if you don't want sample data
initialize_sample_data()
