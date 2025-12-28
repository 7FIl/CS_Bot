import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from handlers.database import get_db_manager
from utils.logger import event_logger
from config import STAFF_NOTIFICATION_CHANNEL_ID, SUPPORT_CHANNEL_ID
import pytz
from datetime import datetime
import asyncio

class SupportModals(commands.Cog):
    """Cog to handle support modals and views."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

class SupportModal(Modal):
    """Modal for users to fill support form."""
    
    def __init__(self):
        super().__init__(
            title="Contact Our Support Team",
            timeout=600  # 10 minutes
        )
        
        self.name_input = TextInput(
            label="Your Name",
            placeholder="Enter your full name",
            required=True,
            max_length=100
        )
        
        self.order_id_input = TextInput(
            label="Order Number / Invoice",
            placeholder="Example: #12345 or INV-2024-001",
            required=True,
            max_length=50
        )
        
        self.issue_type = TextInput(
            label="Issue Type",
            placeholder="Example: Item not arrived, Defect, Payment, etc",
            required=True,
            max_length=100
        )
        
        self.description = TextInput(
            label="Issue Description",
            placeholder="Describe your issue in detail...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.name_input)
        self.add_item(self.order_id_input)
        self.add_item(self.issue_type)
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle submission from modal."""
        try:
            # Defer interaction immediately to prevent timeout (critical for slow operations)
            await interaction.response.defer(ephemeral=True)
            
            # Get data from input
            name = self.name_input.value.strip()
            order_id = self.order_id_input.value.strip()
            issue_type = self.issue_type.value.strip()
            description = self.description.value.strip()
            discord_tag = f"{interaction.user.name}#{interaction.user.discriminator}"
            
            # Save to database (async for better performance)
            db = get_db_manager()
            success, ticket_number = await db.save_lead_async(
                discord_tag=discord_tag,
                name=name,
                order_id=order_id,
                issue_type=issue_type,
                status="PENDING"
            )
            
            if success:
                # Confirm to user
                confirm_embed = discord.Embed(
                    title="✅ Ticket Created Successfully",
                    description="Our support team will contact you soon.",
                    color=discord.Color.green()
                )
                confirm_embed.add_field(name="🎫 Ticket Number", value=f"#{ticket_number}", inline=False)
                confirm_embed.add_field(name="Order ID", value=order_id, inline=False)
                confirm_embed.add_field(name="Issue", value=issue_type, inline=False)
                confirm_embed.add_field(
                    name="Status",
                    value="⏳ Waiting for Support Team",
                    inline=False
                )
                
                # Notify staff and create thread
                thread = await notify_staff(
                    user=interaction.user,
                    name=name,
                    order_id=order_id,
                    issue_type=issue_type,
                    description=description,
                    discord_tag=discord_tag,
                    ticket_number=ticket_number
                )
                
                # Redirect user to their ticket thread
                if thread:
                    confirm_embed.add_field(
                        name="🔗 Ticket Thread",
                        value=f"[Click here to open your ticket]({thread.jump_url})",
                        inline=False
                    )
                
                await interaction.followup.send(embed=confirm_embed, ephemeral=True)
                event_logger.info(f"New ticket created by {discord_tag}: #{ticket_number}")
            else:
                error_embed = discord.Embed(
                    title="❌ An Error Occurred",
                    description="Failed to save data. Please try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                
        except Exception as e:
            event_logger.error(f"Error submitting modal: {str(e)}")
            error_embed = discord.Embed(
                title="❌ An Error Occurred",
                description="An error occurred while processing your request.",
                color=discord.Color.red()
            )
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except:
                pass


async def notify_staff(
    user: discord.User,
    name: str,
    order_id: str,
    issue_type: str,
    description: str,
    discord_tag: str,
    ticket_number: int
):
    """Create private thread in support channel and send notification to staff. Return thread object."""
    try:
        from handlers.commands import bot
        import main
        
        if not bot:
            return
        
        # Get support channel to create thread
        support_channel = bot.get_channel(SUPPORT_CHANNEL_ID)
        if not support_channel:
            event_logger.warning("Support channel not found")
            return
        
        # Get staff notification channel for admin notification
        staff_channel = bot.get_channel(STAFF_NOTIFICATION_CHANNEL_ID)
        if not staff_channel:
            event_logger.warning("Staff notification channel not found")
            return
        
        # Create private thread in support channel (only visible to user, staff, and bot)
        thread_name = f"#{ticket_number} 🎫 {order_id} - {name[:15]}"
        thread = await support_channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.private_thread,
            reason=f"Support ticket #{ticket_number} for {name}"
        )
        
        # Add user to thread
        await thread.add_user(user)
        
        # Format timestamp
        tz = pytz.timezone('Asia/Jakarta')
        now = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
        
        # Prepare embeds (can be done in parallel)
        user_embed = discord.Embed(
            title="📋 Your Support Ticket Details",
            description="Your ticket has been created and our support team will assist you soon.",
            color=discord.Color.blue()
        )
        user_embed.add_field(name="🎫 Ticket Number", value=f"#{ticket_number}", inline=False)
        user_embed.add_field(name="📦 Order ID", value=order_id, inline=False)
        user_embed.add_field(name="👤 Name", value=name, inline=True)
        user_embed.add_field(name="🏷️ Issue Type", value=issue_type, inline=True)
        user_embed.add_field(name="📝 Description", value=description, inline=False)
        user_embed.add_field(name="⏰ Created", value=now, inline=True)
        user_embed.add_field(name="📊 Status", value="⏳ Pending", inline=True)
        user_embed.set_footer(text="Wait for admin to take your ticket")
        
        staff_embed = discord.Embed(
            title="🎫 NEW TICKET RECEIVED",
            description=f"User: {user.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        staff_embed.add_field(name="🎫 Ticket Number", value=f"#{ticket_number}", inline=False)
        staff_embed.add_field(name="👤 Name", value=name, inline=False)
        staff_embed.add_field(name="📦 Order ID", value=order_id, inline=True)
        staff_embed.add_field(name="🏷️ Issue Type", value=issue_type, inline=True)
        staff_embed.add_field(name="📝 Description", value=description[:300] + "..." if len(description) > 300 else description, inline=False)
        staff_embed.add_field(name="👤 Discord Tag", value=discord_tag, inline=True)
        staff_embed.add_field(name="⏰ Time", value=now, inline=True)
        staff_embed.add_field(name="🔗 Thread Link", value=thread.jump_url, inline=False)
        
        # Create views
        view = UnifiedTicketView(user_id=user.id, order_id=order_id, thread_id=thread.id, ticket_number=ticket_number)
        admin_view = StaffTicketView(user_id=user.id, order_id=order_id, thread_id=thread.id, ticket_number=ticket_number)
        
        # Send messages to thread (with error handling)
        try:
            # Send user embed
            await thread.send(embed=user_embed)
            # Send close button view
            await thread.send("You can close this ticket when resolved:", view=view)
        except Exception as thread_error:
            event_logger.error(f"Error sending messages to thread: {str(thread_error)}")
        
        # Get settings from cache (NO DISK READ!)
        try:
            bot_settings = main.get_bot_settings()
            notify_admins = bot_settings.get('notify_admins_on_ticket', True)
        except:
            # Fallback to file read if cache not available
            import json
            import os
            notify_admins = True
            if os.path.exists('bot_settings.json'):
                try:
                    with open('bot_settings.json', 'r') as f:
                        settings = json.load(f)
                        notify_admins = settings.get('notify_admins_on_ticket', True)
                except:
                    pass
        
        # Send notification to staff channel
        if notify_admins:
            # Get admin roles from cache (NO DISK READ!)
            try:
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
            
            admin_mentions = ""
            
            if admin_role_names and staff_channel.guild:
                for role in staff_channel.guild.roles:
                    if role.name in admin_role_names:
                        admin_mentions += f"{role.mention} "
            
            if admin_mentions:
                await staff_channel.send(content=f"🔔 {admin_mentions}", embed=staff_embed, view=admin_view)
            else:
                await staff_channel.send(embed=staff_embed, view=admin_view)
        else:
            await staff_channel.send(embed=staff_embed, view=admin_view)
        
        event_logger.info(f"New ticket created: #{ticket_number} - Order: {order_id} - Private thread: {thread.id}")
        
        return thread
        
    except Exception as e:
        event_logger.error(f"Error notifying staff: {str(e)}")
        return None


class UnifiedTicketView(View):
    """View for user and admin to close ticket with different access levels."""
    
    def __init__(self, user_id: int, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)  # Permanent buttons
        self.user_id = user_id
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
    
    @discord.ui.button(
        label="❌ Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="unified_close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Close ticket - User or Admin with different access."""
        try:
            # Check status from database (OPTIMIZED: direct find instead of pulling 1000 records)
            db = get_db_manager()
            lead = await db.find_lead_by_order_id_async(self.order_id)
            ticket_status = lead.get('status') if lead else None
            
            # Determine if user or admin clicked
            is_user = interaction.user.id == self.user_id
            
            # USER: Can only close if status is still PENDING
            if is_user:
                if ticket_status == 'IN_PROGRESS':
                    await interaction.response.send_message(
                        "❌ Ticket is being handled by staff. Wait for staff to close the ticket.",
                        ephemeral=True
                    )
                    return
                
                await interaction.response.defer()
                
                # Update status to "Closed" (closed by user)
                await db.update_lead_status_async(self.order_id, "Closed")
                
                close_embed = discord.Embed(
                    title="✅ Ticket Closed",
                    description=f"Ticket #{self.ticket_number} has been closed by user.",
                    color=discord.Color.green()
                )
                event_logger.info(f"Ticket #{self.ticket_number} closed by user {interaction.user}")
            
            # ADMIN: Can close anytime
            else:
                await interaction.response.defer()
                
                # Update status to "Resolved" (resolved by admin)
                await db.update_lead_status_async(self.order_id, "Resolved")
                
                close_embed = discord.Embed(
                    title="🔒 Ticket Resolved",
                    description=f"Ticket #{self.ticket_number} has been resolved by {interaction.user.mention}.",
                    color=discord.Color.green()
                )
                event_logger.info(f"Ticket #{self.ticket_number} resolved by admin {interaction.user}")
            
            button.disabled = True
            await interaction.message.edit(view=self)
            
            # Archive and lock thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.send(embed=close_embed)
                await thread.edit(archived=True, locked=True)
            
        except Exception as e:
            event_logger.error(f"Error closing ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to close ticket. Please try again.",
                color=discord.Color.red()
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=error_embed, ephemeral=True)


class StaffTicketView(View):
    """View for staff to take and manage tickets."""
    
    def __init__(self, user_id: int, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)  # Permanent buttons
        self.user_id = user_id
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
        self.staff_member = None  # Track staff who took ticket
    
    @discord.ui.button(
        label="✋ Take Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="staff_take_ticket"
    )
    async def take_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Staff takes the ticket."""
        try:
            # Check ticket status first (OPTIMIZED: direct find instead of pulling 1000 records)
            db = get_db_manager()
            
            # Find specific lead by order_id
            lead = await db.find_lead_by_order_id_async(self.order_id)
            ticket_status = lead.get('status') if lead else None
            
            # If status is not PENDING, ticket is already handled/closed
            if ticket_status and ticket_status != 'PENDING':
                await interaction.response.send_message(
                    f"❌ This ticket cannot be taken anymore (Status: {ticket_status}).",
                    ephemeral=True
                )
                button.disabled = True
                await interaction.message.edit(view=self)
                return
            
            await interaction.response.defer()
            
            staff_member = interaction.user
            user = await interaction.client.fetch_user(self.user_id)
            
            # Update status in database
            db = get_db_manager()
            await db.update_lead_status_async(self.order_id, "IN_PROGRESS")
            
            # Update tracking
            self.staff_member = staff_member.id
            
            # Add staff to thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.add_user(staff_member)
                
                # Send intro message
                intro_embed = discord.Embed(
                    title="👤 Staff Taking Ticket",
                    description=f"Staff {staff_member.mention} has taken your ticket.",
                    color=discord.Color.green()
                )
                intro_embed.add_field(name="📝 Note", 
                    value="Staff will help you resolve this issue.",
                    inline=False)
                
                await thread.send(embed=intro_embed)
            
            # Update notification
            confirmation_embed = discord.Embed(
                title="✅ Ticket Taken",
                description=f"Staff {staff_member.mention} has taken this ticket.",
                color=discord.Color.green()
            )
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            await interaction.message.edit(view=self)
            await interaction.followup.send(embed=confirmation_embed)
            
            event_logger.info(f"Ticket {self.order_id} taken by {staff_member}")
            
        except Exception as e:
            event_logger.error(f"Error staff taking ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to take ticket. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Setup cog."""
    await bot.add_cog(SupportModals(bot))
