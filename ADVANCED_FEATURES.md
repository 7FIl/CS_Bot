"""
Advanced Features Guide
Panduan fitur-fitur lanjutan dan customization
"""

# ============================================================================
# 1. CUSTOMIZING BUTTON & MODAL APPEARANCE
# ============================================================================

"""
Untuk mengubah warna dan style buttons, edit handlers/commands.py:

class SupportMenuView(View):
    @discord.ui.button(
        label="📖 Lihat FAQ",
        style=discord.ButtonStyle.primary,  # primary, secondary, success, danger
        custom_id="view_faq"
    )
    async def view_faq(self, interaction: discord.Interaction, button: Button) -> None:
        ...

Available styles:
- discord.ButtonStyle.primary      → Biru
- discord.ButtonStyle.secondary    → Abu-abu
- discord.ButtonStyle.success      → Hijau
- discord.ButtonStyle.danger       → Merah

Untuk mengubah emoji, edit label parameter.
"""

# ============================================================================
# 2. ADDING NEW FAQ CATEGORIES
# ============================================================================

"""
Di Google Sheets Tab "FAQ":

Tambahkan kolom baru (opsional):
- D: category (untuk kategori: "Harga", "Pengiriman", "Retur", dll)
- E: priority (1-10, untuk urutan tampilan)

Contoh:
trigger_id | button_label | response_text | category | priority
pricing_1  | Berapa Harga? | Harga kami... | Harga | 1
ship_1     | Pengiriman? | Kami kirim... | Pengiriman | 2

Kemudian edit handlers/database.py untuk filter FAQ by category:

def get_faq_by_category(self, category: str) -> list:
    faq_data = self.get_faq_data()
    return [faq for faq in faq_data if faq.get('category') == category]
"""

# ============================================================================
# 3. CUSTOM TICKET STATUS WORKFLOW
# ============================================================================

"""
Default status: PENDING → IN_PROGRESS → RESOLVED

Untuk menambah status custom, edit handlers/modals.py dan database.py:

Status workflow yang bisa ditambahkan:
- PENDING: Baru masuk
- IN_PROGRESS: Sedang ditangani
- ON_HOLD: Menunggu informasi user
- ESCALATED: Escalate ke tier lebih tinggi
- RESOLVED: Selesai
- CLOSED: Ditutup

Update di Tab Leads Google Sheets untuk tracking lebih baik.
"""

# ============================================================================
# 4. IMPLEMENTING PRIORITY TICKETS
# ============================================================================

"""
Edit Modal di handlers/modals.py untuk tambah priority field:

class SupportModal(Modal):
    def __init__(self):
        ...
        self.priority = TextInput(
            label="Prioritas (Rendah/Sedang/Tinggi)",
            placeholder="Pilih: Rendah, Sedang, atau Tinggi",
            required=True,
            max_length=10
        )
        self.add_item(self.priority)

Kemudian update database.py save_lead() untuk include priority.
"""

# ============================================================================
# 5. IMPLEMENTING RATING SYSTEM
# ============================================================================

"""
Tambah tombol rating setelah ticket selesai di private thread:

class RatingView(View):
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.success)
    async def rate_5_stars(self, interaction, button):
        await interaction.response.defer()
        # Simpan rating ke Google Sheets
        db = get_db_manager()
        db.log_rating(order_id, rating=5)

Tambah Tab "Ratings" di Google Sheets untuk tracking satisfaction.
"""

# ============================================================================
# 6. ADDING AUTOMATED MESSAGES
# ============================================================================

"""
Setup scheduled messages yang dikirim otomatis:

Dari main.py:

@tasks.loop(hours=24)
async def daily_report():
    # Setiap hari, kirim report ke notification channel
    db = get_db_manager()
    leads = db.get_all_leads()
    total = len(leads)
    pending = sum(1 for l in leads if l['status'] == 'PENDING')
    
    embed = discord.Embed(title="📊 Daily Report")
    embed.add_field(name="Total Tickets", value=total)
    embed.add_field(name="Pending", value=pending)
    
    channel = bot.get_channel(LOGS_CHANNEL_ID)
    await channel.send(embed=embed)

@daily_report.before_loop
async def before_daily_report():
    await bot.wait_until_ready()
"""

# ============================================================================
# 7. ADDING SEARCH FUNCTIONALITY
# ============================================================================

"""
Command untuk search order:

@commands.command(name='search')
async def search_order(ctx, order_id: str):
    db = get_db_manager()
    leads = db.get_all_leads()
    
    for lead in leads:
        if lead['order_id'] == order_id:
            embed = discord.Embed(title="🔍 Search Result")
            embed.add_field(name="Order", value=lead['order_id'])
            embed.add_field(name="Status", value=lead['status'])
            embed.add_field(name="Issue", value=lead['issue_type'])
            await ctx.send(embed=embed, ephemeral=True)
            return
    
    await ctx.send("Order tidak ditemukan", ephemeral=True)
"""

# ============================================================================
# 8. IMPLEMENTING AUTO-RESPONSE
# ============================================================================

"""
Setup auto-response saat user buat ticket:

Di handlers/modals.py, di method on_submit():

# Kirim auto-response ke user
auto_response = '''
Terima kasih telah menghubungi kami! ✨

Ticket Anda telah kami terima dan akan ditangani dalam:
⏱️ Jam kerja: Max 4 jam (09:00 - 18:00 WIB)
⏱️ Di luar jam kerja: Max 24 jam

Estimasi waktu respon Anda: 2-3 jam

Reference: {order_id}
'''

await user.send(auto_response)
"""

# ============================================================================
# 9. IMPLEMENTING ESCALATION RULES
# ============================================================================

"""
Auto-escalate ticket jika belum resolve dalam waktu tertentu:

Tambah di main.py:

@tasks.loop(hours=1)
async def check_escalation():
    db = get_db_manager()
    leads = db.get_all_leads()
    
    for lead in leads:
        if lead['status'] == 'IN_PROGRESS':
            # Jika lebih dari 24 jam, escalate
            created = datetime.strptime(lead['timestamp'], '%Y-%m-%d %H:%M:%S')
            if datetime.now() - created > timedelta(hours=24):
                db.update_lead_status(lead['order_id'], 'ESCALATED')
                # Notifikasi senior support
                ...
"""

# ============================================================================
# 10. BACKUP & EXPORT FUNCTIONALITY
# ============================================================================

"""
Command untuk backup atau export data:

@commands.command(name='export')
@commands.has_permissions(administrator=True)
async def export_leads(ctx):
    db = get_db_manager()
    leads = db.get_all_leads(limit=1000)
    
    # Convert ke CSV
    import csv
    from datetime import datetime
    
    filename = f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)
    
    # Upload ke Discord
    with open(filename, 'rb') as f:
        await ctx.send(file=discord.File(f, filename))
"""

# ============================================================================
# DEPLOYMENT RECOMMENDATIONS
# ============================================================================

"""
Untuk production deployment, gunakan salah satu:

1. Railway.app
   - Pricing: Free tier available
   - Setup: Connect GitHub, auto-deploy
   - Environment: Add .env variables di dashboard

2. Render.com
   - Pricing: Free tier available
   - Setup: Similar ke Railway
   - Database: Supports multiple services

3. VPS (DigitalOcean, Linode)
   - Pricing: $5/month+
   - Setup: Manual setup
   - Control: Full control

4. Google Cloud Run
   - Pricing: Free tier available
   - Setup: Docker container
   - Scalability: Auto-scale

Rekomendasi: Railway atau Render untuk ease of use
"""

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

"""
1. FAQ Caching
   - FAQ di-cache saat bot startup
   - Minimize Google Sheets API calls
   - Reload hanya saat admin ketik !reload

2. Rate Limiting
   - Add cooldown untuk commands
   - Prevent abuse

   @commands.command()
   @commands.cooldown(1, 60)  # 1 call per 60 seconds
   async def support(ctx):
       ...

3. Async Operations
   - Semua database operations async
   - Prevent blocking event loop

4. Database Connection Pool
   - Reuse Google Sheets connection
   - Don't create new connection per request
"""

# ============================================================================
# MONITORING & ALERTS
# ============================================================================

"""
Setup alerts untuk critical issues:

1. Bot offline detection
2. Database connection failure
3. High number of pending tickets
4. API rate limit approaching

Implementasi:

async def check_health():
    try:
        db = get_db_manager()
        # Test connection
        db.get_faq_data()
    except Exception as e:
        # Send alert ke admin channel
        send_alert_to_admin(f"Database error: {str(e)}")
"""
