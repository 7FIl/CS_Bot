import discord
from discord.ext import commands
from discord.ui import View, Button
from handlers.database import get_db_manager
from handlers.modals import SupportModal
from utils.logger import event_logger
import pytz
from datetime import datetime

bot = None  # Global bot instance for use in modals.py

class SupportCommands(commands.Cog):
    """Commands for support system."""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        global bot
        bot = bot_instance
    
    @commands.command(
        name='support',
        description='Open main support menu',
        help='Display support menu with various help options'
    )
    async def support_menu(self, ctx: commands.Context) -> None:
        """Command to display main support menu."""
        try:
            # Create view with buttons
            view = SupportMenuView()
            
            # Main embed
            embed = discord.Embed(
                title="🎯 Customer Support Center",
                description="Choose one of the options below to get help:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📖 FAQ",
                value="Read answers to frequently asked questions",
                inline=False
            )
            
            embed.add_field(
                name="💬 Chat with Support",
                value="Contact our support team for further assistance",
                inline=False
            )
            
            embed.add_field(
                name="📊 Order Status",
                value="Check your order status",
                inline=False
            )
            
            embed.set_footer(text="💡 Use the buttons below to select an option")
            
            await ctx.send(embed=embed, view=view)
            event_logger.info(f"Support menu displayed by {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error in support command: {str(e)}")
            await ctx.send("❌ An error occurred while opening support menu.", delete_after=10)
    
    @commands.command(
        name='faq',
        description='Display FAQ list',
        help='Display all frequently asked questions'
    )
    async def faq_list(self, ctx: commands.Context) -> None:
        """Command to display FAQ list."""
        try:
            db = get_db_manager()
            faq_data = db.get_faq_data(refresh=True)
            
            if not faq_data:
                embed = discord.Embed(
                    title="📖 FAQ",
                    description="No FAQ available at this time.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed, delete_after=15)
                return
            
            # Create embed for FAQ
            embed = discord.Embed(
                title="📖 Frequently Asked Questions",
                description="Click button to view answer",
                color=discord.Color.green()
            )
            
            # Limit to 25 buttons (Discord UI limit)
            limited_faq = faq_data[:24]
            
            for idx, faq in enumerate(limited_faq, 1):
                button_label = faq.get('button_label', f'FAQ {idx}')[:80]
                embed.add_field(
                    name=f"{idx}. {button_label}",
                    value="Click button to view answer",
                    inline=False
                )
            
            # Create view with FAQ buttons
            view = FAQView(faq_data[:24])
            
            await ctx.send(embed=embed, view=view)
            event_logger.info(f"FAQ list displayed for {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error in faq command: {str(e)}")
            await ctx.send("❌ Failed to load FAQ.", delete_after=10)
    
    @commands.command(
        name='reload',
        description='Reload data from Google Sheets',
        help='Reload FAQ and other data from Google Sheets',
        aliases=['refresh']
    )
    @commands.has_permissions(administrator=True)
    async def reload_data(self, ctx: commands.Context) -> None:
        """Admin command to reload data from Sheets."""
        try:
            db = get_db_manager()
            db.reload_faq_cache()
            
            embed = discord.Embed(
                title="✅ Data Reloaded",
                description="All data successfully reloaded from Google Sheets.",
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed, delete_after=10)
            event_logger.info(f"Data reloaded by {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error in reload command: {str(e)}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to reload data: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=15)
    
    @commands.command(
        name='stats',
        description='Display support statistics',
        help='Display statistics and info about bot'
    )
    @commands.has_permissions(administrator=True)
    async def show_stats(self, ctx: commands.Context) -> None:
        """Admin command to display statistics."""
        try:
            db = get_db_manager()
            leads = db.get_all_leads(limit=100)
            
            # Calculate statistics
            total_leads = len(leads)
            pending_count = sum(1 for lead in leads if lead.get('status') == 'PENDING')
            resolved_count = sum(1 for lead in leads if lead.get('status') == 'RESOLVED')
            
            embed = discord.Embed(
                title="📊 Support Bot Statistics",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="📈 Total Tickets",
                value=str(total_leads),
                inline=True
            )
            embed.add_field(
                name="⏳ Pending",
                value=str(pending_count),
                inline=True
            )
            embed.add_field(
                name="✅ Resolved",
                value=str(resolved_count),
                inline=True
            )
            
            embed.set_footer(text=f"Bot Prefix: {ctx.prefix}")
            
            await ctx.send(embed=embed)
            event_logger.info(f"Stats command used by {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error in stats command: {str(e)}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get statistics.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=15)
    
    @commands.command(
        name='help',
        description='Show help information',
        help='Display all available commands and their descriptions'
    )
    async def help_command(self, ctx: commands.Context, command_name: str = None) -> None:
        """Custom help command."""
        try:
            # Check if user is admin (using cached data - NO DISK READ)
            is_admin = False
            if ctx.guild:
                try:
                    import main
                    admin_role_names = main.get_admin_roles()
                except:
                    # Fallback to file read if cache not available
                    import json
                    import os
                    admin_role_names = []
                    if os.path.exists('admin_roles.json'):
                        try:
                            with open('admin_roles.json', 'r') as f:
                                data = json.load(f)
                                admin_role_names = data.get('admin_roles', [])
                        except:
                            pass
                
                user_role_names = [role.name for role in ctx.author.roles]
                is_admin = any(role_name in admin_role_names for role_name in user_role_names)
            
            if command_name:
                # Show help for specific command
                cmd = self.bot.get_command(command_name)
                if cmd is None:
                    embed = discord.Embed(
                        title="❌ Command Not Found",
                        description=f"No command called '{command_name}' found.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed, delete_after=10)
                    return
                
                # Check if user has permission to view this command
                if cmd.checks and not is_admin:
                    embed = discord.Embed(
                        title="❌ No Permission",
                        description=f"You don't have permission to view this command.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed, delete_after=10)
                    return
                
                embed = discord.Embed(
                    title=f"ℹ️ Help: {ctx.prefix}{cmd.name}",
                    description=cmd.help or "No description available",
                    color=discord.Color.blue()
                )
                
                if cmd.aliases:
                    embed.add_field(
                        name="Aliases",
                        value=", ".join(cmd.aliases),
                        inline=False
                    )
                
                usage = f"{ctx.prefix}{cmd.name}"
                if cmd.signature:
                    usage += f" {cmd.signature}"
                embed.add_field(
                    name="Usage",
                    value=f"`{usage}`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                # Show all commands
                embed = discord.Embed(
                    title="📚 Available Commands",
                    description=f"Use `{ctx.prefix}help <command>` for more info on a specific command.",
                    color=discord.Color.green()
                )
                
                # Get all commands
                commands_list = []
                for command in self.bot.commands:
                    if not command.hidden:
                        commands_list.append(command)
                
                # User commands
                user_commands = [cmd for cmd in commands_list if not cmd.checks]
                if user_commands:
                    user_cmd_text = "\n".join([f"`{ctx.prefix}{cmd.name}` - {cmd.description or 'No description'}" for cmd in user_commands])
                    embed.add_field(
                        name="📖 User Commands",
                        value=user_cmd_text,
                        inline=False
                    )
                
                # Admin commands - only show if user is admin
                if is_admin:
                    admin_commands = [cmd for cmd in commands_list if cmd.checks]
                    if admin_commands:
                        admin_cmd_text = "\n".join([f"`{ctx.prefix}{cmd.name}` - {cmd.description or 'No description'}" for cmd in admin_commands])
                        embed.add_field(
                            name="🔧 Admin Commands",
                            value=admin_cmd_text,
                            inline=False
                        )
                
                embed.set_footer(text=f"Bot Prefix: {ctx.prefix}")
                await ctx.send(embed=embed)
            
            event_logger.info(f"Help command used by {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error in help command: {str(e)}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to display help.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=15)
            
            embed.add_field(
                name="🤖 Bot Info",
                value=f"Prefix: `!`\nVersion: 1.0.2",
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx.author}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            event_logger.error(f"Error in stats command: {str(e)}")
            await ctx.send("❌ Failed to display statistics.", delete_after=10)


class SupportMenuView(View):
    """View for main support menu."""
    
    def __init__(self):
        super().__init__(timeout=600)
    
    @discord.ui.button(
        label="📖 View FAQ",
        style=discord.ButtonStyle.primary,
        custom_id="view_faq"
    )
    async def view_faq(self, interaction: discord.Interaction, button: Button) -> None:
        """Button to view FAQ."""
        try:
            await interaction.response.defer()
            
            db = get_db_manager()
            faq_data = db.get_faq_data()
            
            if not faq_data:
                embed = discord.Embed(
                    title="📖 FAQ",
                    description="No FAQ available.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Send FAQ list
            embed = discord.Embed(
                title="📖 FAQ List",
                description="Select the FAQ you want to view:",
                color=discord.Color.green()
            )
            
            view = FAQView(faq_data[:24])
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            event_logger.error(f"Error in view_faq button: {str(e)}")
    
    @discord.ui.button(
        label="💬 Contact Support",
        style=discord.ButtonStyle.success,
        custom_id="contact_support"
    )
    async def contact_support(self, interaction: discord.Interaction, button: Button) -> None:
        """Button to contact support."""
        try:
            # Display modal
            await interaction.response.send_modal(SupportModal())
            event_logger.info(f"Support modal opened by {interaction.user}")
            
        except Exception as e:
            event_logger.error(f"Error in contact_support button: {str(e)}")
    
    @discord.ui.button(
        label="📊 Check Status",
        style=discord.ButtonStyle.secondary,
        custom_id="check_status"
    )
    async def check_status(self, interaction: discord.Interaction, button: Button) -> None:
        """Button to check order status."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="📊 Check Order Status",
                description="This feature is under development.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="💡 Tips",
                value="Contact our support for your order status information.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            event_logger.error(f"Error in check_status button: {str(e)}")


class FAQView(View):
    """View to display FAQ buttons."""
    
    def __init__(self, faq_data: list):
        super().__init__(timeout=600)
        self.faq_data = faq_data
        
        # Add buttons for each FAQ (max 25)
        for idx, faq in enumerate(faq_data[:24]):
            button_label = faq.get('button_label', f'FAQ {idx + 1}')[:80]
            trigger_id = str(faq.get('trigger_id', f'faq_{idx}'))
            
            button = Button(
                label=button_label,
                style=discord.ButtonStyle.secondary,
                custom_id=f"faq_{trigger_id}_{idx}"
            )
            button.callback = self.create_faq_callback(faq)
            self.add_item(button)
    
    def create_faq_callback(self, faq: dict):
        """Create callback for FAQ button."""
        async def faq_callback(interaction: discord.Interaction) -> None:
            try:
                await interaction.response.defer(ephemeral=True)
                
                question = faq.get('button_label', 'Question')
                answer = faq.get('response_text', 'Answer not available.')
                
                embed = discord.Embed(
                    title=f"❓ {question}",
                    description=answer,
                    color=discord.Color.green()
                )
                
                embed.set_footer(text="FAQ Support Bot")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                event_logger.info(f"FAQ viewed by {interaction.user}: {question}")
                
            except Exception as e:
                event_logger.error(f"Error in FAQ callback: {str(e)}")
        
        return faq_callback


async def setup(bot: commands.Bot) -> None:
    """Setup cog."""
    await bot.add_cog(SupportCommands(bot))
