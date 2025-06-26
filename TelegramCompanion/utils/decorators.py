import logging
from functools import wraps
from aiogram import types
from config import ADMIN_IDS, BOT_MESSAGES

logger = logging.getLogger(__name__)

def admin_required(func):
    """Decorator to restrict access to admin-only functions."""
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "Unknown"
            first_name = message.from_user.first_name or "Unknown"
            
            if user_id not in ADMIN_IDS:
                await message.reply(BOT_MESSAGES['unauthorized'])
                logger.warning(f"Unauthorized admin access attempt by user {user_id} (@{username})")
                return
            # User is authorized, proceed with the function
            return await func(message, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in admin_required decorator: {e}")
            await message.reply("❌ Authorization error occurred")
    
    return wrapper

def log_user_action(action_name: str):
    """Decorator to log user actions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            try:
                user_id = message.from_user.id
                username = message.from_user.username or "Unknown"
                logger.info(f"User {user_id} (@{username}) performed action: {action_name}")
                return await func(message, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in log_user_action decorator: {e}")
                raise
        return wrapper
    return decorator
