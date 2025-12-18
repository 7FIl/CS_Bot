import discord
from discord.ext import commands
from handlers.database import get_db_manager
from utils.logger import event_logger, bot_logger
from config import LOGS_CHANNEL_ID

class Events(commands.Cog):
    """Event handlers untuk bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Event ketika bot berhasil login."""
        try:
            bot_logger.info(f"✅ Bot logged in as {self.bot.user}")
            bot_logger.info(f"Bot ID: {self.bot.user.id}")
            bot_logger.info(f"Bot is in {len(self.bot.guilds)} server(s)")
            
            # Set status
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="Customer Support | !support"
            )
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
            
            # Initialize database
            try:
                db = get_db_manager()
                bot_logger.info("✅ Database (Google Sheets) connected")
            except Exception as e:
                bot_logger.error(f"❌ Failed to connect database: {str(e)}")
            
        except Exception as e:
            event_logger.error(f"Error di on_ready: {str(e)}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle command errors."""
        try:
            if isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(
                    title="❌ Argument Kurang",
                    description=f"Gunakan: `!{ctx.command.name} {ctx.command.signature}`",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
            
            elif isinstance(error, commands.CommandNotFound):
                # Silent ignore
                pass
            
            elif isinstance(error, commands.MissingPermissions):
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="Anda tidak memiliki permission untuk command ini.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
            
            else:
                event_logger.error(f"Command error: {str(error)}")
                embed = discord.Embed(
                    title="❌ Error",
                    description="Terjadi error saat memproses command Anda.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
        
        except Exception as e:
            event_logger.error(f"Error di error handler: {str(e)}")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event ketika bot join server baru."""
        try:
            bot_logger.info(f"Bot joined new server: {guild.name} (ID: {guild.id})")
            event_logger.info(f"New server joined: {guild.name}")
        except Exception as e:
            event_logger.error(f"Error di on_guild_join: {str(e)}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event ketika bot di-remove dari server."""
        try:
            bot_logger.warning(f"Bot removed from server: {guild.name} (ID: {guild.id})")
            event_logger.warning(f"Server removed: {guild.name}")
        except Exception as e:
            event_logger.error(f"Error di on_guild_remove: {str(e)}")

async def setup(bot: commands.Bot) -> None:
    """Setup cog."""
    await bot.add_cog(Events(bot))
