import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from handlers.user_handlers import register_user_handlers
from handlers.admin_handlers import register_admin_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def main():
    """Main function to start the bot."""
    try:
        # Register handlers
        register_user_handlers(dp, bot)
        register_admin_handlers(dp, bot)
        
        logger.info("Starting Yene Gebeya Telegram Bot...")
        
        # Start polling
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
