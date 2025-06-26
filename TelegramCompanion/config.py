import os
import logging

# Bot configuration
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Admin configuration
ADMIN_IDS = [7007277566]  # Admin Telegram user IDs

# Payment method information
PAYMENT_METHODS = {
    "telebirr": "Telebirr: 0915794686 / 091283132",
    "mpesa": "M-Pesa: 0777991328",
    "cbe": "CBE: 1000463082085 Hana Tasew",
    "dashen": "Dashen Bank: (Send to admin)",
    "coop": "Coop Bank: 1000082245867 Hana Tasew"
}

# Bot messages
BOT_MESSAGES = {
    'welcome': "👋 Welcome to Yene Gebeya! Choose a category:",
    'cart_empty': "🧵 Your cart is empty.",
    'cart_header': "🛺 Your Cart:\n",
    'total_label': "\n💵 Total: {total} ETB",
    'payment_prompt': "💳 Choose your payment method:",
    'order_processing': "📦 Your order is being processed. We'll contact you shortly!",
    'contact_info': "☎️ Contact us at: @Ztech7 or 0915794686",
    'help_text': "ℹ️ How to shop:\n1. Choose a category\n2. View products\n3. Add to cart\n4. Buy now and pay\n5. Track with /myorder",
    'unauthorized': "⛔ Not authorized.",
    'category_exists': "⚠️ Category already exists.",
    'category_added': "✅ Category '{category}' added.",
    'product_added': "✅ Product '{name}' added under '{category}'.",
    'product_format_error': "❌ Format:\n/add_product Name | Price | Desc | Image | Category",
    'added_to_cart': "✅ Added to cart!",
    'payment_selected': "✅ Selected: {method}\n{info}\n\nAfter payment, use /myorder to track your delivery."
}

# Validate configuration
if API_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logging.warning("Bot token not set! Please set TELEGRAM_BOT_TOKEN environment variable.")
