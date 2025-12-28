"""
Discord Customer Support Bot with Google Sheets Integration
Bot for managing customer support with admin panel in Google Sheets

Author: 7Fil
Version: 1.0.2
"""

import discord
from discord.ext import commands
import asyncio
import os
import json
from config import DISCORD_TOKEN, PREFIX, DEBUG_MODE, DISCORD_GUILD_ID
from utils.logger import bot_logger
from handlers.database import init_db_manager

# Global cache for JSON files (to avoid repeated disk reads)
_json_cache = {
    'admin_roles': None,
    'bot_settings': None
}

def load_json_cache():
    """Load JSON files into memory cache on bot startup."""
    global _json_cache
    
    # Load admin_roles.json
    try:
        if os.path.exists('admin_roles.json'):
            with open('admin_roles.json', 'r') as f:
                _json_cache['admin_roles'] = json.load(f)
                bot_logger.info(f"✅ Cached admin_roles.json: {len(_json_cache['admin_roles'].get('admin_roles', []))} roles")
        else:
            _json_cache['admin_roles'] = {'admin_roles': []}
            bot_logger.warning("⚠️  admin_roles.json not found, using empty cache")
    except Exception as e:
        bot_logger.error(f"❌ Error loading admin_roles.json: {e}")
        _json_cache['admin_roles'] = {'admin_roles': []}
    
    # Load bot_settings.json
    try:
        if os.path.exists('bot_settings.json'):
            with open('bot_settings.json', 'r') as f:
                _json_cache['bot_settings'] = json.load(f)
                bot_logger.info(f"✅ Cached bot_settings.json")
        else:
            _json_cache['bot_settings'] = {'notify_admins_on_ticket': True}
            bot_logger.warning("⚠️  bot_settings.json not found, using defaults")
    except Exception as e:
        bot_logger.error(f"❌ Error loading bot_settings.json: {e}")
        _json_cache['bot_settings'] = {'notify_admins_on_ticket': True}

def get_admin_roles() -> list:
    """Get admin roles from cache."""
    return _json_cache.get('admin_roles', {}).get('admin_roles', [])

def get_bot_settings() -> dict:
    """Get bot settings from cache."""
    return _json_cache.get('bot_settings', {'notify_admins_on_ticket': True})

def reload_json_cache():
    """Reload JSON cache (call this after file changes)."""
    load_json_cache()

# Configure Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.dm_messages = True

# Initialize Discord bot
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    debug=DEBUG_MODE,
    help_command=None  # Disable default help command (we'll create custom one)
)

async def load_cogs():
    """Load all cogs from handlers directory."""
    cogs_dir = 'handlers'
    
    # Get list of loaded extensions to avoid reloading
    loaded_extensions = [ext for ext in bot.extensions.keys()]
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            
            # Skip database.py as it's a module, not a cog
            if cog_name == 'database':
                continue
            
            extension_name = f'{cogs_dir}.{cog_name}'
            
            # Skip if already loaded
            if extension_name in loaded_extensions:
                bot_logger.info(f"⏭️  Skipped (already loaded): {cog_name}")
                continue
            
            try:
                await bot.load_extension(extension_name)
                bot_logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                bot_logger.error(f"❌ Failed to load cog {cog_name}: {str(e)}")

async def main():
    """Main function to run the bot."""
    try:
        bot_logger.info("=" * 50)
        bot_logger.info("🤖 Initializing Discord Customer Support Bot")
        bot_logger.info("=" * 50)
        
        # Load JSON cache
        bot_logger.info("📋 Loading JSON cache...")
        load_json_cache()
        
        # Initialize database
        bot_logger.info("📊 Connecting to Google Sheets...")
        try:
            db_manager = init_db_manager()
            bot_logger.info("✅ Database connected successfully")
        except Exception as e:
            bot_logger.error(f"❌ Failed to connect database: {str(e)}")
            bot_logger.error("Please check your credentials.json file")
            return
        
        # Load cogs
        bot_logger.info("📦 Loading cogs...")
        await load_cogs()
        
        # Start bot
        bot_logger.info("🚀 Starting bot...")
        await bot.start(DISCORD_TOKEN)
    
    except Exception as e:
        bot_logger.error(f"❌ Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    # Only run directly if not imported by GUI
    print("=" * 60)
    print("Note: You can now use gui_app.py for a graphical interface!")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.info("⏹️  Bot stopped by user")
    except Exception as e:
        bot_logger.error(f"❌ Fatal error: {str(e)}")

