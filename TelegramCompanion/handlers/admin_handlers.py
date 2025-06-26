import logging
from aiogram import Bot, Dispatcher, types
from config import BOT_MESSAGES
from data.storage import categories, products, pending_payments
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

def register_admin_handlers(dp: Dispatcher, bot: Bot):
    """Register all admin-related handlers."""
    
    @dp.message_handler(commands=['add_category'])
    @admin_required
    async def add_category(message: types.Message):
        """Add a new product category (Admin only)."""
        try:
            # Extract category name from command
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.reply("❌ Usage: /add_category <category_name>")
                return
                
            category = command_parts[1].strip()
            
            if not category:
                await message.reply("❌ Category name cannot be empty")
                return
                
            # Check if category already exists (case insensitive)
            if any(cat.lower() == category.lower() for cat in categories):
                await message.reply(BOT_MESSAGES['category_exists'])
                return
            
            # Add category
            categories.append(category)
            await message.reply(BOT_MESSAGES['category_added'].format(category=category))
            logger.info(f"Category '{category}' added by admin {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in add_category: {e}")
            await message.reply("❌ Error adding category. Please try again.")

    @dp.message_handler(commands=['add_product'])
    @admin_required
    async def add_product(message: types.Message):
        """Add a new product (Admin only)."""
        try:
            # Extract product data from command
            command_text = message.text[len("/add_product "):].strip()
            
            if not command_text:
                await message.reply(BOT_MESSAGES['product_format_error'])
                return
            
            # Parse product data
            parts = [part.strip() for part in command_text.split('|')]
            
            if len(parts) != 5:
                await message.reply(BOT_MESSAGES['product_format_error'])
                return
            
            name, price_str, description, image, category = parts
            
            # Validate inputs
            if not all([name, price_str, description, image, category]):
                await message.reply("❌ All fields are required and cannot be empty")
                return
            
            # Validate price
            try:
                price = int(price_str)
                if price <= 0:
                    await message.reply("❌ Price must be a positive number")
                    return
            except ValueError:
                await message.reply("❌ Price must be a valid number")
                return
            
            # Check if category exists
            if not any(cat.lower() == category.lower() for cat in categories):
                await message.reply(f"❌ Category '{category}' does not exist. Please add it first using /add_category")
                return
            
            # Generate new product ID
            new_id = max([p['id'] for p in products], default=0) + 1
            
            # Create product
            new_product = {
                "id": new_id,
                "name": name,
                "price": price,
                "description": description,
                "image": image,
                "category": category,
                "stock": 10  # Default stock amount
            }
            
            products.append(new_product)
            
            await message.reply(BOT_MESSAGES['product_added'].format(name=name, category=category))
            logger.info(f"Product '{name}' added by admin {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in add_product: {e}")
            await message.reply("❌ Error adding product. Please check the format and try again.")

    @dp.message_handler(commands=['list_categories'])
    @admin_required
    async def list_categories(message: types.Message):
        """List all categories (Admin only)."""
        try:
            if not categories:
                await message.reply("📦 No categories found.")
                return
            
            category_list = "\n".join([f"• {cat}" for cat in categories])
            await message.reply(f"📦 **Categories:**\n{category_list}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in list_categories: {e}")
            await message.reply("❌ Error listing categories")

    @dp.message_handler(commands=['list_products'])
    @admin_required
    async def list_products(message: types.Message):
        """List all products (Admin only)."""
        try:
            if not products:
                await message.reply("📦 No products found.")
                return
            
            product_list = []
            for product in products:
                stock_info = f" | Stock: {product.get('stock', 0)}"
                product_list.append(
                    f"ID: {product['id']} | {product['name']} | {product['price']} ETB | {product['category']}{stock_info}"
                )
            
            products_text = "\n".join(product_list)
            await message.reply(f"📦 **Products:**\n{products_text}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in list_products: {e}")
            await message.reply("❌ Error listing products")

    @dp.message_handler(commands=['remove_product'])
    @admin_required
    async def remove_product(message: types.Message):
        """Remove a product by ID (Admin only)."""
        try:
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.reply("❌ Usage: /remove_product <product_id>")
                return
            
            try:
                product_id = int(command_parts[1].strip())
            except ValueError:
                await message.reply("❌ Product ID must be a number")
                return
            
            # Find and remove product
            product_to_remove = None
            for i, product in enumerate(products):
                if product['id'] == product_id:
                    product_to_remove = products.pop(i)
                    break
            
            if product_to_remove:
                await message.reply(f"✅ Product '{product_to_remove['name']}' removed successfully")
                logger.info(f"Product ID {product_id} removed by admin {message.from_user.id}")
            else:
                await message.reply(f"❌ Product with ID {product_id} not found")
                
        except Exception as e:
            logger.error(f"Error in remove_product: {e}")
            await message.reply("❌ Error removing product")

    @dp.message_handler(commands=['admin_help'])
    @admin_required
    async def admin_help(message: types.Message):
        """Show admin commands (Admin only)."""
        try:
            help_text = """
🔧 **Admin Commands:**

📦 **Category Management:**
• /add_category <name> - Add new category
• /list_categories - List all categories

🛍️ **Product Management:**
• /add_product Name | Price | Description | Image | Category
• /list_products - List all products
• /remove_product <id> - Remove product by ID

ℹ️ **Other:**
• /admin_help - Show this help
            """
            await message.reply(help_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_help: {e}")
            await message.reply("❌ Error loading admin help")

    @dp.message_handler(commands=['update_stock'])
    @admin_required
    async def update_stock(message: types.Message):
        """Update product stock (Admin only)."""
        try:
            command_parts = message.text.split(' ')
            if len(command_parts) < 3:
                await message.reply("❌ Usage: /update_stock <product_id> <new_stock>")
                return
            
            try:
                product_id = int(command_parts[1])
                new_stock = int(command_parts[2])
            except ValueError:
                await message.reply("❌ Product ID and stock must be numbers")
                return
            
            # Find and update product
            product = None
            for p in products:
                if p['id'] == product_id:
                    p['stock'] = max(0, new_stock)
                    product = p
                    break
            
            if product:
                await message.reply(f"✅ Stock updated for '{product['name']}': {product['stock']} units")
                logger.info(f"Stock updated for product ID {product_id} by admin {message.from_user.id}")
            else:
                await message.reply(f"❌ Product with ID {product_id} not found")
                
        except Exception as e:
            logger.error(f"Error in update_stock: {e}")
            await message.reply("❌ Error updating stock")

    @dp.message_handler(commands=['pending_orders'])
    @admin_required
    async def pending_orders(message: types.Message):
        """View pending orders (Admin only)."""
        try:
            if not pending_payments:
                await message.reply("📦 No pending orders.")
                return
            
            orders_text = "📋 **Pending Orders:**\n\n"
            for order_id, order in pending_payments.items():
                if order['status'] == 'pending_approval':
                    orders_text += f"🆔 {order_id}\n"
                    orders_text += f"👤 {order['first_name']} (@{order['username']})\n"
                    orders_text += f"💰 {order['total']} ETB via {order['payment_method'].upper()}\n"
                    orders_text += f"📱 User ID: {order['user_id']}\n\n"
            
            await message.reply(orders_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in pending_orders: {e}")
            await message.reply("❌ Error loading pending orders")

    @dp.callback_query_handler(lambda c: c.data.startswith('approve_'))
    @admin_required
    async def approve_order(callback_query: types.CallbackQuery):
        """Approve an order (Admin only)."""
        try:
            order_id = callback_query.data.split('_')[1]
            
            if order_id not in pending_payments:
                await bot.answer_callback_query(callback_query.id, text="❌ Order not found")
                return
            
            order = pending_payments[order_id]
            
            # Update order status
            order['status'] = 'approved'
            
            # Reduce stock for ordered items
            for item in order['items']:
                for product in products:
                    if product['id'] == item['id']:
                        product['stock'] = max(0, product.get('stock', 0) - 1)
                        break
            
            # Clear user cart
            if order['user_id'] in cart:
                cart[order['user_id']] = []
            
            # Notify customer
            customer_message = f"✅ ORDER APPROVED!\n\n"
            customer_message += f"📋 Order ID: {order_id}\n"
            customer_message += f"💰 Total: {order['total']} ETB\n"
            customer_message += f"📦 Your order is now being prepared for shipment.\n"
            customer_message += f"🚚 You will receive shipping updates soon.\n\n"
            customer_message += f"Thank you for shopping with Yene Gebeya!"
            
            await bot.send_message(order['user_id'], customer_message)
            
            # Update admin message
            await bot.edit_message_text(
                f"✅ APPROVED\n\nOrder {order_id} has been approved.\nStock has been reduced.\nCustomer has been notified.",
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            
            await bot.answer_callback_query(callback_query.id, text=f"✅ Order {order_id} approved")
            logger.info(f"Order {order_id} approved by admin {callback_query.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in approve_order: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error approving order")

    @dp.callback_query_handler(lambda c: c.data.startswith('decline_'))
    @admin_required
    async def decline_order(callback_query: types.CallbackQuery):
        """Decline an order (Admin only)."""
        try:
            order_id = callback_query.data.split('_')[1]
            
            if order_id not in pending_payments:
                await bot.answer_callback_query(callback_query.id, text="❌ Order not found")
                return
            
            order = pending_payments[order_id]
            
            # Update order status
            order['status'] = 'declined'
            
            # Notify customer
            customer_message = f"❌ ORDER DECLINED\n\n"
            customer_message += f"📋 Order ID: {order_id}\n"
            customer_message += f"💰 Total: {order['total']} ETB\n"
            customer_message += f"🔄 Your payment was not verified.\n"
            customer_message += f"📞 Please contact us at @Ztech7 for assistance.\n\n"
            customer_message += f"You can try placing a new order with correct payment proof."
            
            await bot.send_message(order['user_id'], customer_message)
            
            # Update admin message
            await bot.edit_message_text(
                f"❌ DECLINED\n\nOrder {order_id} has been declined.\nCustomer has been notified.",
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            
            await bot.answer_callback_query(callback_query.id, text=f"❌ Order {order_id} declined")
            logger.info(f"Order {order_id} declined by admin {callback_query.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in decline_order: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error declining order")

    @dp.message_handler(commands=['update_order_status'])
    @admin_required
    async def update_order_status(message: types.Message):
        """Update order status (Admin only)."""
        try:
            command_parts = message.text.split(' ')
            if len(command_parts) < 3:
                await message.reply("❌ Usage: /update_order_status <order_id> <status>\nStatuses: preparing, shipped, delivered")
                return
            
            order_id = command_parts[1]
            new_status = command_parts[2].lower()
            
            valid_statuses = ['preparing', 'shipped', 'delivered']
            if new_status not in valid_statuses:
                await message.reply(f"❌ Invalid status. Valid statuses: {', '.join(valid_statuses)}")
                return
            
            if order_id not in pending_payments:
                await message.reply(f"❌ Order {order_id} not found")
                return
            
            order = pending_payments[order_id]
            old_status = order['status']
            order['status'] = new_status
            
            # Notify customer of status update
            status_messages = {
                'preparing': f"📦 Order {order_id} is being prepared for shipment.",
                'shipped': f"🚚 Order {order_id} has been shipped! Your items are on the way.",
                'delivered': f"🏠 Order {order_id} has been delivered! Thank you for shopping with Yene Gebeya!"
            }
            
            customer_message = f"📊 ORDER STATUS UPDATE\n\n"
            customer_message += f"📋 Order ID: {order_id}\n"
            customer_message += f"📊 Status: {new_status.title()}\n\n"
            customer_message += status_messages.get(new_status, "Your order status has been updated.")
            
            await bot.send_message(order['user_id'], customer_message)
            
            await message.reply(f"✅ Order {order_id} status updated from '{old_status}' to '{new_status}'\nCustomer has been notified.")
            logger.info(f"Order {order_id} status updated to {new_status} by admin {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error in update_order_status: {e}")
            await message.reply("❌ Error updating order status")
