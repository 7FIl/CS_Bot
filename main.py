"""
Discord Customer Support Bot dengan Google Sheets Integration
Bot untuk mengelola customer support dengan admin panel di Google Sheets

Author: Your Name
Version: 1.0.0
"""

import discord
from discord.ext import commands
import asyncio
import os
from config import DISCORD_TOKEN, PREFIX, DEBUG_MODE, DISCORD_GUILD_ID
from utils.logger import bot_logger
from handlers.database import init_db_manager

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.dm_messages = True

# Bot initialization
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    debug=DEBUG_MODE,
    help_command=commands.DefaultHelpCommand()
)

async def load_cogs():
    """Load semua cogs dari handlers directory."""
    cogs_dir = 'handlers'
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            
            # Skip database.py karena itu module, bukan cog
            if cog_name == 'database':
                continue
            
            try:
                await bot.load_extension(f'{cogs_dir}.{cog_name}')
                bot_logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                bot_logger.error(f"❌ Failed to load cog {cog_name}: {str(e)}")

async def main():
    """Main function untuk menjalankan bot."""
    try:
        bot_logger.info("=" * 50)
        bot_logger.info("🤖 Initializing Discord Customer Support Bot")
        bot_logger.info("=" * 50)
        
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.info("⏹️  Bot stopped by user")
    except Exception as e:
        bot_logger.error(f"❌ Fatal error: {str(e)}")
