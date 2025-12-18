import discord
from discord.ext import commands
from discord.ui import View, Button
from handlers.database import get_db_manager
from handlers.modals import SupportModal
from utils.logger import event_logger
import pytz
from datetime import datetime

bot = None  # Global bot instance untuk digunakan di modals.py

class SupportCommands(commands.Cog):
    """Commands untuk support system."""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        global bot
        bot = bot_instance
    
    @commands.command(
        name='support',
        description='Buka menu support utama',
        help='Tampilkan menu support dengan berbagai pilihan bantuan'
    )
    async def support_menu(self, ctx: commands.Context) -> None:
        """Command untuk menampilkan menu support utama."""
        try:
            # Buat view dengan buttons
            view = SupportMenuView()
            
            # Embed utama
            embed = discord.Embed(
                title="🎯 Pusat Support Pelanggan",
                description="Pilih salah satu opsi di bawah untuk mendapatkan bantuan:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📖 FAQ",
                value="Baca jawaban dari pertanyaan yang sering diajukan",
                inline=False
            )
            
            embed.add_field(
                name="💬 Chat dengan Support",
                value="Hubungi tim support kami untuk bantuan lebih lanjut",
                inline=False
            )
            
            embed.add_field(
                name="📊 Status Order",
                value="Cek status order Anda",
                inline=False
            )
            
            embed.set_footer(text="💡 Gunakan button di bawah untuk memilih opsi")
            
            await ctx.send(embed=embed, view=view)
            event_logger.info(f"Support menu ditampilkan oleh {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error di support command: {str(e)}")
            await ctx.send("❌ Terjadi error saat membuka support menu.", delete_after=10)
    
    @commands.command(
        name='faq',
        description='Tampilkan daftar FAQ',
        help='Tampilkan semua pertanyaan yang sering diajukan'
    )
    async def faq_list(self, ctx: commands.Context) -> None:
        """Command untuk menampilkan daftar FAQ."""
        try:
            db = get_db_manager()
            faq_data = db.get_faq_data(refresh=True)
            
            if not faq_data:
                embed = discord.Embed(
                    title="📖 FAQ",
                    description="Tidak ada FAQ yang tersedia saat ini.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed, delete_after=15)
                return
            
            # Buat embed untuk FAQ
            embed = discord.Embed(
                title="📖 Daftar Pertanyaan yang Sering Diajukan",
                description="Klik button untuk melihat jawaban",
                color=discord.Color.green()
            )
            
            # Limit maksimal 25 buttons (Discord UI limit)
            limited_faq = faq_data[:24]
            
            for idx, faq in enumerate(limited_faq, 1):
                button_label = faq.get('button_label', f'FAQ {idx}')[:80]
                embed.add_field(
                    name=f"{idx}. {button_label}",
                    value="Klik button untuk melihat jawaban",
                    inline=False
                )
            
            # Buat view dengan FAQ buttons
            view = FAQView(faq_data[:24])
            
            await ctx.send(embed=embed, view=view)
            event_logger.info(f"FAQ list ditampilkan untuk {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error di faq command: {str(e)}")
            await ctx.send("❌ Gagal memuat FAQ.", delete_after=10)
    
    @commands.command(
        name='reload',
        description='Reload data dari Google Sheets',
        help='Reload FAQ dan data lainnya dari Google Sheets',
        aliases=['refresh']
    )
    @commands.has_permissions(administrator=True)
    async def reload_data(self, ctx: commands.Context) -> None:
        """Command admin untuk reload data dari Sheets."""
        try:
            db = get_db_manager()
            db.reload_faq_cache()
            
            embed = discord.Embed(
                title="✅ Data Reloaded",
                description="Semua data berhasil di-reload dari Google Sheets.",
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed, delete_after=10)
            event_logger.info(f"Data reloaded oleh {ctx.author}")
            
        except Exception as e:
            event_logger.error(f"Error di reload command: {str(e)}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"Gagal reload data: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=15)
    
    @commands.command(
        name='stats',
        description='Tampilkan statistik support',
        help='Tampilkan statistik dan info tentang bot'
    )
    @commands.has_permissions(administrator=True)
    async def show_stats(self, ctx: commands.Context) -> None:
        """Command admin untuk menampilkan statistik."""
        try:
            db = get_db_manager()
            leads = db.get_all_leads(limit=100)
            
            # Hitung statistik
            total_leads = len(leads)
            pending_count = sum(1 for lead in leads if lead.get('status') == 'PENDING')
            resolved_count = sum(1 for lead in leads if lead.get('status') == 'RESOLVED')
            
            embed = discord.Embed(
                title="📊 Statistik Support Bot",
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
            
            embed.add_field(
                name="🤖 Bot Info",
                value=f"Prefix: `!`\nVersion: 1.0.0",
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx.author}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            event_logger.error(f"Error di stats command: {str(e)}")
            await ctx.send("❌ Gagal menampilkan statistik.", delete_after=10)


class SupportMenuView(View):
    """View untuk support menu utama."""
    
    def __init__(self):
        super().__init__(timeout=600)
    
    @discord.ui.button(
        label="📖 Lihat FAQ",
        style=discord.ButtonStyle.primary,
        custom_id="view_faq"
    )
    async def view_faq(self, interaction: discord.Interaction, button: Button) -> None:
        """Button untuk melihat FAQ."""
        try:
            await interaction.response.defer()
            
            db = get_db_manager()
            faq_data = db.get_faq_data()
            
            if not faq_data:
                embed = discord.Embed(
                    title="📖 FAQ",
                    description="Tidak ada FAQ tersedia.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Kirim FAQ list
            embed = discord.Embed(
                title="📖 Daftar FAQ",
                description="Pilih FAQ yang ingin Anda lihat:",
                color=discord.Color.green()
            )
            
            view = FAQView(faq_data[:24])
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            event_logger.error(f"Error di view_faq button: {str(e)}")
    
    @discord.ui.button(
        label="💬 Hubungi Support",
        style=discord.ButtonStyle.success,
        custom_id="contact_support"
    )
    async def contact_support(self, interaction: discord.Interaction, button: Button) -> None:
        """Button untuk hubungi support."""
        try:
            # Tampilkan modal
            await interaction.response.send_modal(SupportModal())
            event_logger.info(f"Support modal dibuka oleh {interaction.user}")
            
        except Exception as e:
            event_logger.error(f"Error di contact_support button: {str(e)}")
    
    @discord.ui.button(
        label="📊 Cek Status",
        style=discord.ButtonStyle.secondary,
        custom_id="check_status"
    )
    async def check_status(self, interaction: discord.Interaction, button: Button) -> None:
        """Button untuk cek status order."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="📊 Cek Status Order",
                description="Fitur ini sedang dalam pengembangan.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="💡 Tips",
                value="Hubungi support kami untuk info status order Anda.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            event_logger.error(f"Error di check_status button: {str(e)}")


class FAQView(View):
    """View untuk menampilkan FAQ buttons."""
    
    def __init__(self, faq_data: list):
        super().__init__(timeout=600)
        self.faq_data = faq_data
        
        # Add buttons untuk setiap FAQ (max 25)
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
        """Create callback untuk FAQ button."""
        async def faq_callback(interaction: discord.Interaction) -> None:
            try:
                await interaction.response.defer(ephemeral=True)
                
                question = faq.get('button_label', 'Pertanyaan')
                answer = faq.get('response_text', 'Jawaban tidak tersedia.')
                
                embed = discord.Embed(
                    title=f"❓ {question}",
                    description=answer,
                    color=discord.Color.green()
                )
                
                embed.set_footer(text="FAQ Support Bot")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                event_logger.info(f"FAQ dilihat oleh {interaction.user}: {question}")
                
            except Exception as e:
                event_logger.error(f"Error di FAQ callback: {str(e)}")
        
        return faq_callback


async def setup(bot: commands.Bot) -> None:
    """Setup cog."""
    await bot.add_cog(SupportCommands(bot))
