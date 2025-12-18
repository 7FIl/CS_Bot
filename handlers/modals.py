import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from handlers.database import get_db_manager
from utils.logger import event_logger
from config import STAFF_NOTIFICATION_CHANNEL_ID, SUPPORT_CHANNEL_ID
import pytz
from datetime import datetime

class SupportModals(commands.Cog):
    """Cog untuk handle support modals dan views."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

class SupportModal(Modal):
    """Modal untuk user mengisi formulir support."""
    
    def __init__(self):
        super().__init__(
            title="Hubungi Tim Support Kami",
            timeout=600  # 10 menit
        )
        
        self.name_input = TextInput(
            label="Nama Anda",
            placeholder="Masukkan nama lengkap Anda",
            required=True,
            max_length=100
        )
        
        self.order_id_input = TextInput(
            label="Nomor Order / Invoice",
            placeholder="Contoh: #12345 atau INV-2024-001",
            required=True,
            max_length=50
        )
        
        self.issue_type = TextInput(
            label="Tipe Masalah",
            placeholder="Contoh: Barang belum sampai, Cacat, Pembayaran, dll",
            required=True,
            max_length=100
        )
        
        self.description = TextInput(
            label="Deskripsi Masalah",
            placeholder="Jelaskan masalah Anda secara detail...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.name_input)
        self.add_item(self.order_id_input)
        self.add_item(self.issue_type)
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle submission dari modal."""
        try:
            # Defer interaction
            await interaction.response.defer(ephemeral=True)
            
            # Ambil data dari input
            name = self.name_input.value.strip()
            order_id = self.order_id_input.value.strip()
            issue_type = self.issue_type.value.strip()
            description = self.description.value.strip()
            discord_tag = f"{interaction.user.name}#{interaction.user.discriminator}"
            
            # Simpan ke database
            db = get_db_manager()
            success, ticket_number = db.save_lead(
                discord_tag=discord_tag,
                name=name,
                order_id=order_id,
                issue_type=issue_type,
                status="PENDING"
            )
            
            if success:
                # Konfirmasi ke user
                confirm_embed = discord.Embed(
                    title="✅ Ticket Dibuat Berhasil",
                    description="Tim support kami akan menghubungi Anda segera.",
                    color=discord.Color.green()
                )
                confirm_embed.add_field(name="🎫 Nomor Ticket", value=f"#{ticket_number}", inline=False)
                confirm_embed.add_field(name="Order ID", value=order_id, inline=False)
                confirm_embed.add_field(name="Masalah", value=issue_type, inline=False)
                confirm_embed.add_field(
                    name="Status",
                    value="⏳ Menunggu Tim Support",
                    inline=False
                )
                
                # Notifikasi ke staff dan buat thread
                thread = await notify_staff(
                    user=interaction.user,
                    name=name,
                    order_id=order_id,
                    issue_type=issue_type,
                    description=description,
                    discord_tag=discord_tag,
                    ticket_number=ticket_number
                )
                
                # Redirect user ke thread ticket mereka
                if thread:
                    confirm_embed.add_field(
                        name="🔗 Thread Ticket",
                        value=f"[Klik di sini untuk membuka ticket Anda]({thread.jump_url})",
                        inline=False
                    )
                
                await interaction.followup.send(embed=confirm_embed, ephemeral=True)
                event_logger.info(f"Ticket baru dibuat oleh {discord_tag}: #{ticket_number}")
            else:
                error_embed = discord.Embed(
                    title="❌ Terjadi Kesalahan",
                    description="Gagal menyimpan data. Silakan coba lagi.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                
        except Exception as e:
            event_logger.error(f"Error saat submit modal: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Terjadi Kesalahan",
                description="Terjadi error saat memproses request Anda.",
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
    """Buat private thread di support channel dan kirim notifikasi ke staff. Return thread object."""
    try:
        from handlers.commands import bot
        
        if not bot:
            return
        
        # Ambil support channel untuk membuat thread
        support_channel = bot.get_channel(SUPPORT_CHANNEL_ID)
        if not support_channel:
            event_logger.warning(f"Support channel tidak ditemukan")
            return
        
        # Ambil staff notification channel untuk notifikasi admin
        staff_channel = bot.get_channel(STAFF_NOTIFICATION_CHANNEL_ID)
        if not staff_channel:
            event_logger.warning(f"Staff notification channel tidak ditemukan")
            return
        
        # Buat private thread di support channel (hanya bisa dilihat oleh user, staff, dan bot)
        thread_name = f"#{ticket_number} 🎫 {order_id} - {name[:15]}"
        thread = await support_channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.private_thread,
            reason=f"Support ticket #{ticket_number} untuk {name}"
        )
        
        # Add user ke thread
        await thread.add_user(user)
        
        # Format timestamp
        tz = pytz.timezone('Asia/Jakarta')
        now = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
        
        # Kirim ticket info ke thread untuk user
        user_embed = discord.Embed(
            title="📋 Detail Ticket Support Anda",
            description="Ticket Anda telah dibuat dan tim support kami akan segera membantu.",
            color=discord.Color.blue()
        )
        user_embed.add_field(name="🎫 Nomor Ticket", value=f"#{ticket_number}", inline=False)
        user_embed.add_field(name="📦 Order ID", value=order_id, inline=False)
        user_embed.add_field(name="👤 Nama", value=name, inline=True)
        user_embed.add_field(name="🏷️ Tipe Masalah", value=issue_type, inline=True)
        user_embed.add_field(name="📝 Deskripsi", value=description, inline=False)
        user_embed.add_field(name="⏰ Waktu Dibuat", value=now, inline=True)
        user_embed.add_field(name="📊 Status", value="⏳ Pending", inline=True)
        user_embed.set_footer(text="Tunggu sampai admin mengambil ticket Anda")
        
        await thread.send(embed=user_embed)
        
        # Kirim view dengan unified close button (untuk user dan admin)
        view = UnifiedTicketView(user_id=user.id, order_id=order_id, thread_id=thread.id, ticket_number=ticket_number)
        await thread.send("Anda dapat menutup ticket ini jika sudah selesai:", view=view)
        
        # Kirim notifikasi ke staff channel dengan admin buttons
        staff_embed = discord.Embed(
            title="🎫 TICKET BARU MASUK",
            description=f"User: {user.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        staff_embed.add_field(name="🎫 Nomor Ticket", value=f"#{ticket_number}", inline=False)
        staff_embed.add_field(name="👤 Nama", value=name, inline=False)
        staff_embed.add_field(name="📦 Order ID", value=order_id, inline=True)
        staff_embed.add_field(name="🏷️ Tipe Masalah", value=issue_type, inline=True)
        staff_embed.add_field(name="📝 Deskripsi", value=description[:300] + "..." if len(description) > 300 else description, inline=False)
        staff_embed.add_field(name="👤 Discord Tag", value=discord_tag, inline=True)
        staff_embed.add_field(name="⏰ Waktu", value=now, inline=True)
        staff_embed.add_field(name="🔗 Link Thread", value=thread.jump_url, inline=False)
        
        # Buat view dengan admin buttons
        admin_view = StaffTicketView(user_id=user.id, order_id=order_id, thread_id=thread.id, ticket_number=ticket_number)
        
        await staff_channel.send(embed=staff_embed, view=admin_view)
        event_logger.info(f"Ticket baru dibuat: #{ticket_number} - Order: {order_id} - Private thread: {thread.id}")
        
        return thread
        
    except Exception as e:
        event_logger.error(f"Error saat notify staff: {str(e)}")
        return None


class UnifiedTicketView(View):
    """View untuk user dan admin menutup ticket dengan akses berbeda."""
    
    def __init__(self, user_id: int, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)  # Permanent buttons
        self.user_id = user_id
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
    
    @discord.ui.button(
        label="❌ Tutup Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="unified_close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Tutup ticket - User atau Admin dengan akses berbeda."""
        try:
            # Check status dari database
            db = get_db_manager()
            all_leads = db.get_all_leads(limit=1000)
            ticket_status = None
            for lead in all_leads:
                if str(lead.get('order_id', '')).strip() == str(self.order_id).strip():
                    ticket_status = lead.get('status')
                    break
            
            # Tentukan apakah user atau admin yang klik
            is_user = interaction.user.id == self.user_id
            
            # USER: Hanya bisa close jika status masih PENDING
            if is_user:
                if ticket_status == 'IN_PROGRESS':
                    await interaction.response.send_message(
                        "❌ Ticket sedang ditangani oleh staff. Tunggu staff untuk menutup ticket.",
                        ephemeral=True
                    )
                    return
                
                await interaction.response.defer()
                
                # Update status ke "Closed" (ditutup oleh user)
                db.update_lead_status(self.order_id, "Closed")
                
                close_embed = discord.Embed(
                    title="✅ Ticket Ditutup",
                    description=f"Ticket #{self.ticket_number} telah ditutup oleh user.",
                    color=discord.Color.green()
                )
                event_logger.info(f"Ticket #{self.ticket_number} ditutup oleh user {interaction.user}")
            
            # ADMIN: Bisa close kapan saja
            else:
                await interaction.response.defer()
                
                # Update status ke "Resolved" (diselesaikan oleh admin)
                db.update_lead_status(self.order_id, "Resolved")
                
                close_embed = discord.Embed(
                    title="🔒 Ticket Diselesaikan",
                    description=f"Ticket #{self.ticket_number} telah diselesaikan oleh {interaction.user.mention}.",
                    color=discord.Color.green()
                )
                event_logger.info(f"Ticket #{self.ticket_number} diselesaikan oleh admin {interaction.user}")
            
            button.disabled = True
            await interaction.message.edit(view=self)
            
            # Archive dan lock thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.send(embed=close_embed)
                await thread.edit(archived=True, locked=True)
            
        except Exception as e:
            event_logger.error(f"Error saat close ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Gagal menutup ticket. Silakan coba lagi.",
                color=discord.Color.red()
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=error_embed, ephemeral=True)


class UserTicketView(View):
    """View untuk user menutup ticket mereka sendiri."""
    
    def __init__(self, user_id: int, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)  # Permanent buttons
        self.user_id = user_id
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
        self.staff_member = None  # Track jika ada staff yang ambil
    
    @discord.ui.button(
        label="❌ Tutup Ticket Saya",
        style=discord.ButtonStyle.danger,
        custom_id="user_close_ticket"
    )
    async def user_close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """User menutup ticket mereka sendiri (hanya jika belum diambil staff)."""
        try:
            # Pastikan hanya user yang bisa close ticket mereka
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "❌ Hanya pemilik ticket yang bisa menutup ticket ini!",
                    ephemeral=True
                )
                return
            
            # Check status dari database - jika sudah IN_PROGRESS, staff sudah ambil
            db = get_db_manager()
            all_leads = db.get_all_leads(limit=1000)
            ticket_status = None
            for lead in all_leads:
                if str(lead.get('order_id', '')).strip() == str(self.order_id).strip():
                    ticket_status = lead.get('status')
                    break
            
            # Jika status sudah IN_PROGRESS, staff sudah ambil - user tidak boleh close
            if ticket_status == 'IN_PROGRESS':
                await interaction.response.send_message(
                    "❌ Ticket sedang ditangani oleh staff. Tunggu staff untuk menutup ticket.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer()
            
            # Update status di database ke "Closed" (ditutup oleh user)
            db.update_lead_status(self.order_id, "Closed")
            
            # Update embed dan disable button
            close_embed = discord.Embed(
                title="✅ Ticket Ditutup",
                description=f"Ticket #{self.ticket_number} telah ditutup oleh user.",
                color=discord.Color.green()
            )
            
            button.disabled = True
            await interaction.message.edit(view=self)
            
            # Archive dan lock thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.send(embed=close_embed)
                await thread.edit(archived=True, locked=True)
            
            event_logger.info(f"Ticket #{self.ticket_number} ditutup oleh user {interaction.user}")
            
        except Exception as e:
            event_logger.error(f"Error saat user close ticket: {str(e)}")


class StaffTicketView(View):
    """View untuk staff mengambil dan mengelola ticket."""
    
    def __init__(self, user_id: int, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)  # Permanent buttons
        self.user_id = user_id
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
        self.staff_member = None  # Track staff yang ambil
    
    @discord.ui.button(
        label="✋ Ambil Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="staff_take_ticket"
    )
    async def take_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Staff mengambil ticket."""
        try:
            # Check status ticket terlebih dahulu
            db = get_db_manager()
            
            # Get all leads dan cari dengan order_id
            all_leads = db.get_all_leads(limit=1000)
            ticket_status = None
            for lead in all_leads:
                if str(lead.get('order_id', '')).strip() == str(self.order_id).strip():
                    ticket_status = lead.get('status')
                    break
            
            # Jika status bukan PENDING, ticket sudah dihandle/ditutup
            if ticket_status and ticket_status != 'PENDING':
                await interaction.response.send_message(
                    f"❌ Ticket ini sudah tidak dapat diambil (Status: {ticket_status}).",
                    ephemeral=True
                )
                button.disabled = True
                await interaction.message.edit(view=self)
                return
            
            await interaction.response.defer()
            
            staff_member = interaction.user
            user = await interaction.client.fetch_user(self.user_id)
            
            # Update status di database
            db = get_db_manager()
            db.update_lead_status(self.order_id, "IN_PROGRESS")
            
            # Update tracking
            self.staff_member = staff_member.id
            
            # Add staff ke thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.add_user(staff_member)
                
                # Send intro message
                intro_embed = discord.Embed(
                    title="👤 Staff Mengambil Ticket",
                    description=f"Staff {staff_member.mention} telah mengambil ticket Anda.",
                    color=discord.Color.green()
                )
                intro_embed.add_field(name="📝 Keterangan", 
                    value="Staff akan membantu Anda menyelesaikan masalah ini.",
                    inline=False)
                
                await thread.send(embed=intro_embed)
                
                # Update unified button message (button sudah ada di thread dari awal)
            
            # Update notification
            confirmation_embed = discord.Embed(
                title="✅ Ticket Diambil",
                description=f"Staff {staff_member.mention} telah mengambil ticket ini.",
                color=discord.Color.green()
            )
            
            # Disable take button, disable user close button
            button.disabled = True
            
            # Disable semua buttons
            for item in self.children:
                item.disabled = True
            
            await interaction.message.edit(view=self)
            await interaction.followup.send(embed=confirmation_embed)
            
            event_logger.info(f"Ticket {self.order_id} diambil oleh {staff_member}")
            
        except Exception as e:
            event_logger.error(f"Error saat staff take ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Gagal mengambil ticket. Silakan coba lagi.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)


class AdminCloseTicketView(View):
    """View untuk admin menutup ticket (hanya di thread)."""
    
    def __init__(self, order_id: str, thread_id: int, ticket_number: int = 0):
        super().__init__(timeout=None)
        self.order_id = order_id
        self.thread_id = thread_id
        self.ticket_number = ticket_number
    
    @discord.ui.button(
        label="🔒 Selesaikan Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="admin_close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Admin menutup ticket (hanya bisa di thread)."""
        try:
            await interaction.response.defer()
            
            # Update status di database ke "Resolved" (diselesaikan oleh admin)
            db = get_db_manager()
            db.update_lead_status(self.order_id, "Resolved")
            
            # Update button
            close_embed = discord.Embed(
                title="🔒 Ticket Diselesaikan",
                description=f"Ticket #{self.ticket_number} telah diselesaikan oleh {interaction.user.mention}.",
                color=discord.Color.green()
            )
            
            button.disabled = True
            await interaction.message.edit(view=self)
            
            # Archive thread
            thread = interaction.client.get_channel(self.thread_id)
            if thread:
                await thread.send(embed=close_embed)
                await thread.edit(archived=True, locked=True)
            
            event_logger.info(f"Ticket #{self.ticket_number} diselesaikan oleh {interaction.user}")
            
        except Exception as e:
            event_logger.error(f"Error saat close ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Gagal menutup ticket. Silakan coba lagi.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)


class TicketActionView(View):
    """View untuk staff mengambil ticket."""
    
    def __init__(self, user_id: int, order_id: str):
        super().__init__(timeout=3600)  # 1 jam
        self.user_id = user_id
        self.order_id = order_id
    
    @discord.ui.button(
        label="✋ Ambil Ticket",
        style=discord.ButtonStyle.primary,  
        custom_id="take_ticket_button"
    )
    async def take_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Handle ketika staff ambil ticket."""
        try:
            await interaction.response.defer()
            
            staff_member = interaction.user
            user = await interaction.client.fetch_user(self.user_id)
            
            # Update status di database
            db = get_db_manager()
            db.update_lead_status(self.order_id, "IN_PROGRESS")
            
            # Buat private thread
            thread_name = f"🎫 {self.order_id[:10]} - {user.name}"
            thread = await interaction.channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.private_thread,
                reason=f"Support ticket {self.order_id}"
            )
            
            # Add staff dan user ke thread
            await thread.add_user(staff_member)
            await thread.add_user(user)
            
            # Kirim intro message ke thread
            intro_embed = discord.Embed(
                title="Ticket Support Dibuka",
                description=f"Staff: {staff_member.mention}\nUser: {user.mention}",
                color=discord.Color.blue()
            )
            intro_embed.add_field(name="Order ID", value=self.order_id, inline=False)
            
            await thread.send(embed=intro_embed)
            
            # Update message di notification channel
            confirmation_embed = discord.Embed(
                title="✅ Ticket Diambil",
                description=f"Staff {staff_member.mention} telah mengambil ticket ini.",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=confirmation_embed)
            
            # Disable button
            button.disabled = True
            await interaction.message.edit(view=self)
            
            event_logger.info(f"Ticket {self.order_id} diambil oleh {staff_member}")
            
        except Exception as e:
            event_logger.error(f"Error saat ambil ticket: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Gagal mengambil ticket. Silakan coba lagi.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    @discord.ui.button(
        label="❌ Tutup Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        """Handle ketika ticket ditutup."""
        try:
            await interaction.response.defer()
            
            # Update status
            db = get_db_manager()
            db.update_lead_status(self.order_id, "RESOLVED")
            
            close_embed = discord.Embed(
                title="❌ Ticket Ditutup",
                description=f"Order {self.order_id} telah ditutup.",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=close_embed)
            
            event_logger.info(f"Ticket {self.order_id} ditutup")
            
        except Exception as e:
            event_logger.error(f"Error saat tutup ticket: {str(e)}")
            
        except Exception as e:
            event_logger.error(f"Error saat tutup ticket: {str(e)}")


async def setup(bot: commands.Bot) -> None:
    """Setup cog."""
    await bot.add_cog(SupportModals(bot))
