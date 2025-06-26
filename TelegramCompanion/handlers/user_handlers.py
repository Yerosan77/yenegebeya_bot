import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import BOT_MESSAGES, PAYMENT_METHODS, ADMIN_IDS
from data.storage import categories, products, cart, pending_payments, order_counter

logger = logging.getLogger(__name__)

class OrderState(StatesGroup):
    waiting_for_payment_method = State()
    waiting_for_payment_proof = State()

def register_user_handlers(dp: Dispatcher, bot: Bot):
    """Register all user-related handlers."""
    
    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        """Handle /start command."""
        try:
            keyboard = InlineKeyboardMarkup()
            
            # Add category buttons
            for cat in categories:
                keyboard.add(InlineKeyboardButton(f"📦 {cat}", callback_data=f"cat_{cat}"))
            
            # Add utility buttons
            keyboard.add(
                InlineKeyboardButton("🛺 My Cart", callback_data="cart"),
                InlineKeyboardButton("📦 My Order", callback_data="order"),
            )
            keyboard.add(
                InlineKeyboardButton("☎️ Contact", callback_data="contact"),
                InlineKeyboardButton("📘 Help", callback_data="help")
            )
            
            await message.answer(BOT_MESSAGES['welcome'], reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error in send_welcome: {e}")
            await message.answer("❌ Something went wrong. Please try again.")

    @dp.callback_query_handler(lambda c: c.data.startswith('cat_'))
    async def show_products(callback_query: types.CallbackQuery):
        """Show products for selected category."""
        try:
            category = callback_query.data[4:]
            filtered_products = [p for p in products if p['category'].lower() == category.lower()]
            
            if not filtered_products:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"📦 No products found in category '{category}'"
                )
                await bot.answer_callback_query(callback_query.id)
                return
            
            for product in filtered_products:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(
                    InlineKeyboardButton("💼 Add to Cart", callback_data=f"add_{product['id']}")
                )
                
                stock_info = f"\n📦 Stock: {product.get('stock', 0)} available" if product.get('stock', 0) > 0 else "\n❌ Out of Stock"
                caption = f"**{product['name']}**\n💵 {product['price']} ETB{stock_info}\n\n{product['description']}"
                
                try:
                    await bot.send_photo(
                        callback_query.from_user.id,
                        product['image'],
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                except Exception as img_error:
                    # If image fails, send text message
                    logger.warning(f"Failed to send image for product {product['id']}: {img_error}")
                    await bot.send_message(
                        callback_query.from_user.id,
                        caption,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
            
            await bot.answer_callback_query(callback_query.id)
            
        except Exception as e:
            logger.error(f"Error in show_products: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error loading products")

    @dp.callback_query_handler(lambda c: c.data.startswith('add_'))
    async def add_to_cart(callback_query: types.CallbackQuery):
        """Add product to cart."""
        try:
            user_id = callback_query.from_user.id
            product_id = int(callback_query.data.split('_')[1])
            
            # Verify product exists and has stock
            product = next((p for p in products if p['id'] == product_id), None)
            if not product:
                await bot.answer_callback_query(callback_query.id, text="❌ Product not found")
                return
            
            if product.get('stock', 0) <= 0:
                await bot.answer_callback_query(callback_query.id, text="❌ Product out of stock")
                return
            
            # Add to cart
            if user_id not in cart:
                cart[user_id] = []
            cart[user_id].append(product_id)
            
            await bot.answer_callback_query(callback_query.id, text=BOT_MESSAGES['added_to_cart'])
            
        except Exception as e:
            logger.error(f"Error in add_to_cart: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error adding to cart")

    @dp.callback_query_handler(lambda c: c.data == 'cart')
    async def show_cart(callback_query: types.CallbackQuery):
        """Show user's cart contents."""
        try:
            user_id = callback_query.from_user.id
            cart_items = cart.get(user_id, [])
            
            if not cart_items:
                await bot.send_message(user_id, BOT_MESSAGES['cart_empty'])
                await bot.answer_callback_query(callback_query.id)
                return
            
            total = 0
            message = BOT_MESSAGES['cart_header']
            
            for item_id in cart_items:
                product = next((p for p in products if p['id'] == item_id), None)
                if product:
                    message += f"- {product['name']} ({product['price']} ETB)\n"
                    total += product['price']
            
            message += BOT_MESSAGES['total_label'].format(total=total)
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🛒 Buy Now", callback_data="checkout"))
            keyboard.add(InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart"))
            
            await bot.send_message(user_id, message, reply_markup=keyboard)
            await bot.answer_callback_query(callback_query.id)
            
        except Exception as e:
            logger.error(f"Error in show_cart: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error loading cart")

    @dp.callback_query_handler(lambda c: c.data == 'clear_cart')
    async def clear_cart_handler(callback_query: types.CallbackQuery):
        """Clear user's cart."""
        try:
            user_id = callback_query.from_user.id
            cart[user_id] = []
            await bot.send_message(user_id, "🗑️ Cart cleared!")
            await bot.answer_callback_query(callback_query.id)
            
        except Exception as e:
            logger.error(f"Error in clear_cart: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error clearing cart")

    @dp.callback_query_handler(lambda c: c.data == 'checkout')
    async def checkout(callback_query: types.CallbackQuery):
        """Start checkout process."""
        try:
            user_id = callback_query.from_user.id
            cart_items = cart.get(user_id, [])
            
            if not cart_items:
                await bot.send_message(user_id, BOT_MESSAGES['cart_empty'])
                await bot.answer_callback_query(callback_query.id)
                return
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr"),
                InlineKeyboardButton("💰 M-Pesa", callback_data="pay_mpesa")
            )
            keyboard.add(
                InlineKeyboardButton("🏦 CBE", callback_data="pay_cbe"),
                InlineKeyboardButton("🏛️ Dashen", callback_data="pay_dashen")
            )
            keyboard.add(
                InlineKeyboardButton("🤝 Coop Bank", callback_data="pay_coop")
            )
            
            await bot.send_message(user_id, BOT_MESSAGES['payment_prompt'], reply_markup=keyboard)
            await OrderState.waiting_for_payment_method.set()
            await bot.answer_callback_query(callback_query.id)
            
        except Exception as e:
            logger.error(f"Error in checkout: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error starting checkout")

    @dp.callback_query_handler(lambda c: c.data.startswith("pay_"), state=OrderState.waiting_for_payment_method)
    async def handle_payment(callback_query: types.CallbackQuery, state: FSMContext):
        """Handle payment method selection."""
        try:
            global order_counter
            method = callback_query.data.split("_")[1]
            user_id = callback_query.from_user.id
            username = callback_query.from_user.username or "Unknown"
            first_name = callback_query.from_user.first_name or "Unknown"
            
            # Calculate total and prepare order
            cart_items = cart.get(user_id, [])
            total = 0
            order_details = []
            
            for item_id in cart_items:
                product = next((p for p in products if p['id'] == item_id), None)
                if product:
                    order_details.append({
                        'id': product['id'],
                        'name': product['name'],
                        'price': product['price']
                    })
                    total += product['price']
            
            # Generate order ID
            order_id = f"ORD{order_counter}"
            order_counter += 1
            
            # Store pending payment
            pending_payments[order_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'items': order_details,
                'total': total,
                'payment_method': method,
                'status': 'pending_proof'
            }
            
            # Store order ID in state for next step
            await state.update_data(order_id=order_id)
            
            payment_info = PAYMENT_METHODS.get(method, "Payment method not available")
            
            message = f"✅ Order Created: {order_id}\n"
            message += f"💰 Total: {total} ETB\n\n"
            message += f"📱 Payment Method: {method.upper()}\n"
            message += f"{payment_info}\n\n"
            message += "📸 Please send a screenshot or photo of your payment confirmation to complete your order."
            
            await bot.send_message(user_id, message)
            await OrderState.waiting_for_payment_proof.set()
            await bot.answer_callback_query(callback_query.id)
            
        except Exception as e:
            logger.error(f"Error in handle_payment: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error processing payment")
            await state.finish()

    @dp.message_handler(content_types=['photo'], state=OrderState.waiting_for_payment_proof)
    async def handle_payment_proof(message: types.Message, state: FSMContext):
        """Handle payment proof upload."""
        try:
            user_data = await state.get_data()
            order_id = user_data.get('order_id')
            
            if not order_id or order_id not in pending_payments:
                await message.reply("❌ Order not found. Please start checkout again.")
                await state.finish()
                return
            
            order = pending_payments[order_id]
            
            # Update order status
            order['status'] = 'pending_approval'
            order['payment_proof'] = message.photo[-1].file_id
            
            # Notify user
            await message.reply(f"✅ Payment proof received for order {order_id}!\n📋 Your order is pending admin approval.\n🔔 You will be notified once approved.")
            
            # Notify admin with approval buttons
            admin_message = f"🔔 NEW ORDER - PENDING APPROVAL\n\n"
            admin_message += f"📋 Order ID: {order_id}\n"
            admin_message += f"👤 Customer: {order['first_name']} (@{order['username']})\n"
            admin_message += f"💰 Total: {order['total']} ETB\n"
            admin_message += f"💳 Payment: {order['payment_method'].upper()}\n\n"
            admin_message += "📦 Items:\n"
            
            for item in order['items']:
                admin_message += f"• {item['name']} - {item['price']} ETB\n"
            
            admin_message += f"\n📱 Customer ID: {order['user_id']}"
            
            # Create approval buttons
            approval_keyboard = InlineKeyboardMarkup()
            approval_keyboard.add(
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{order_id}"),
                InlineKeyboardButton("❌ Decline", callback_data=f"decline_{order_id}")
            )
            
            # Send to all admins
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, admin_message, reply_markup=approval_keyboard)
                    await bot.send_photo(admin_id, message.photo[-1].file_id, caption=f"Payment Proof for Order {order_id}")
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
            
            await state.finish()
            
        except Exception as e:
            logger.error(f"Error in handle_payment_proof: {e}")
            await message.reply("❌ Error processing payment proof")
            await state.finish()

    @dp.message_handler(state=OrderState.waiting_for_payment_proof)
    async def handle_invalid_payment_proof(message: types.Message, state: FSMContext):
        """Handle non-photo messages during payment proof upload."""
        await message.reply("📸 Please send a photo/screenshot of your payment confirmation.")

    @dp.message_handler(commands=['myorder'])
    async def track_order(message: types.Message):
        """Handle order tracking."""
        try:
            user_id = message.from_user.id
            user_orders = []
            
            # Find user's orders
            for order_id, order in pending_payments.items():
                if order['user_id'] == user_id:
                    user_orders.append((order_id, order))
            
            if not user_orders:
                await message.reply("📦 You have no orders yet.")
                return
            
            orders_text = "📋 **Your Orders:**\n\n"
            for order_id, order in user_orders:
                status_emoji = {
                    'pending_approval': '⏳',
                    'approved': '✅',
                    'preparing': '📦',
                    'shipped': '🚚',
                    'delivered': '🏠',
                    'declined': '❌'
                }.get(order['status'], '❓')
                
                status_text = {
                    'pending_approval': 'Pending Payment Approval',
                    'approved': 'Payment Approved - Preparing Order',
                    'preparing': 'Preparing for Shipment',
                    'shipped': 'Shipped - On the Way',
                    'delivered': 'Delivered',
                    'declined': 'Payment Declined'
                }.get(order['status'], 'Unknown Status')
                
                orders_text += f"{status_emoji} **{order_id}**\n"
                orders_text += f"💰 {order['total']} ETB\n"
                orders_text += f"📊 Status: {status_text}\n\n"
            
            await message.reply(orders_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in track_order: {e}")
            await message.reply("❌ Error tracking order")

    @dp.callback_query_handler(lambda c: c.data == 'order')
    async def show_order_inline(callback_query: types.CallbackQuery):
        """Handle order tracking via inline button."""
        try:
            await bot.send_message(
                callback_query.from_user.id,
                BOT_MESSAGES['order_processing']
            )
            await bot.answer_callback_query(callback_query.id)
        except Exception as e:
            logger.error(f"Error in show_order_inline: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error tracking order")

    @dp.callback_query_handler(lambda c: c.data == 'contact')
    async def show_contact(callback_query: types.CallbackQuery):
        """Show contact information."""
        try:
            await bot.send_message(
                callback_query.from_user.id,
                BOT_MESSAGES['contact_info']
            )
            await bot.answer_callback_query(callback_query.id)
        except Exception as e:
            logger.error(f"Error in show_contact: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error loading contact info")

    @dp.callback_query_handler(lambda c: c.data == 'help')
    async def show_help(callback_query: types.CallbackQuery):
        """Show help information."""
        try:
            await bot.send_message(
                callback_query.from_user.id,
                BOT_MESSAGES['help_text']
            )
            await bot.answer_callback_query(callback_query.id)
        except Exception as e:
            logger.error(f"Error in show_help: {e}")
            await bot.answer_callback_query(callback_query.id, text="❌ Error loading help")

    @dp.message_handler(commands=['myid'])
    async def show_my_id(message: types.Message):
        """Show user's Telegram ID."""
        try:
            await message.reply(f"🆔 Your Telegram ID is: {message.from_user.id}")
        except Exception as e:
            logger.error(f"Error in show_my_id: {e}")
            await message.reply("❌ Error getting your ID")
