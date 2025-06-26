# Yene Gebeya Telegram Bot

## Overview

This is a Telegram e-commerce bot called "Yene Gebeya" (My Market in Amharic) built using Python and the aiogram framework. The bot enables users to browse products by category, add items to cart, and complete purchases through various Ethiopian payment methods. It includes both user-facing shopping functionality and admin controls for product management.

## System Architecture

The bot follows a modular, handler-based architecture using the aiogram framework:

- **Bot Core**: Main bot instance using aiogram v2.25.1 with memory-based storage
- **Handler System**: Separate modules for user and admin functionality
- **In-Memory Storage**: Simple Python data structures for products, categories, and shopping carts
- **State Management**: FSM (Finite State Machine) for order processing workflows
- **Authorization**: Role-based access control for admin functions

## Key Components

### Core Files
- `bot.py`: Main entry point, initializes bot and registers handlers
- `config.py`: Configuration management including tokens, admin IDs, and payment methods
- `handlers/user_handlers.py`: User-facing functionality (browsing, cart, orders)
- `handlers/admin_handlers.py`: Admin controls for category and product management
- `data/storage.py`: In-memory data storage with sample data initialization
- `utils/decorators.py`: Security and logging decorators

### Handler Architecture
- **User Handlers**: Product browsing, cart management, order placement
- **Admin Handlers**: Category creation, product addition (admin-only)
- **Callback Handlers**: Inline keyboard interactions for product selection
- **State Management**: Order processing with payment method selection

### Security Layer
- Admin authorization via decorator pattern
- User action logging for audit trails
- Input validation and error handling

## Data Flow

1. **User Journey**: Start → Browse Categories → View Products → Add to Cart → Select Payment → Order Tracking
2. **Admin Workflow**: Authentication → Add Categories → Add Products → Monitor Activity
3. **State Management**: FSM handles order processing states and payment method selection
4. **Data Persistence**: In-memory storage (suitable for development, needs database for production)

## External Dependencies

### Core Dependencies
- **aiogram 2.25.1**: Telegram Bot API framework
- **Python 3.11**: Runtime environment

### Payment Integration
- Multiple Ethiopian payment methods configured:
  - Telebirr
  - M-Pesa
  - Commercial Bank of Ethiopia (CBE)
  - Dashen Bank
  - Cooperative Bank of Oromia

## Deployment Strategy

- **Platform**: Replit with Python 3.11 environment
- **Process Management**: Workflow-based execution with pip dependency installation
- **Environment Variables**: Bot token via `TELEGRAM_BOT_TOKEN`
- **Startup**: Automatic dependency installation and bot polling initiation

### Production Considerations
- Current in-memory storage should be replaced with persistent database
- Environment-specific configuration management needed
- Error monitoring and logging infrastructure required

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- June 23, 2025: Initial bot setup with modular architecture
- June 23, 2025: Bot deployed and running successfully on Telegram (@yenegebeya_bot)
- June 23, 2025: Admin functionality fully tested and working
- June 23, 2025: User @Ztech7 (ID: 7007277566) confirmed as admin
- June 23, 2025: Product and category management tested successfully
- June 23, 2025: Shopping experience with Ethiopian payment methods active
- June 23, 2025: Complete order approval system implemented with admin review workflow
- June 23, 2025: Order tracking system with status updates from payment to delivery
- June 23, 2025: Stock management with automatic reduction only after admin approval

## Admin Commands

Your Telegram ID (7007277566) is configured as admin. You can use these commands in the bot:

**Category Management:**
- `/add_category Electronics` - Add new category
- `/list_categories` - Show all categories

**Product Management:**
- `/add_product iPhone 14 | 25000 | Latest smartphone with great camera | https://example.com/image.jpg | Electronics`
- `/list_products` - Show all products with IDs
- `/remove_product 1` - Remove product by ID

**Help:**
- `/admin_help` - Show admin command reference