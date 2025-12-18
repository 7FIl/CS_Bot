"""
Installation & First Run Guide
Panduan instalasi dan menjalankan bot untuk pertama kali
"""

# ============================================================================
# STEP 1: VERIFY PYTHON VERSION
# ============================================================================

"""
1. Buka Command Prompt / PowerShell
2. Run: python --version
3. Harus Python 3.10 atau lebih tinggi

Jika belum punya Python:
- Download dari https://www.python.org/downloads/
- Install dan pastikan add Python to PATH
- Restart command prompt
"""

# ============================================================================
# STEP 2: INSTALL DEPENDENCIES
# ============================================================================

"""
1. Navigate ke project folder:
   cd C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot

2. Install requirements:
   pip install -r requirements.txt

   Ini akan install:
   - discord.py (Discord bot framework)
   - gspread (Google Sheets API)
   - oauth2client (Google authentication)
   - python-dotenv (Environment variables)
   - pandas (Data handling)
   - pytz (Timezone handling)

3. Verify install:
   pip list
   
   Cek semua package terinstall
"""

# ============================================================================
# STEP 3: SETUP GOOGLE SHEETS
# ============================================================================

"""
Follow SETUP_GUIDE.md untuk:
1. Create project di Google Cloud Console
2. Enable Google Sheets & Drive API
3. Create Service Account
4. Download credentials.json
5. Share Google Sheets dengan Service Account
6. Copy Sheet ID ke .env

Expected result:
- File credentials.json di project root
- Google Sheets shared dan accessible
"""

# ============================================================================
# STEP 4: CREATE GOOGLE SHEETS STRUCTURE
# ============================================================================

"""
1. Buka https://sheets.google.com
2. Create new spreadsheet (or use existing)
3. Rename default sheet menjadi "FAQ"
4. Buat struktur:

Tab 1 - FAQ:
Row 1 (Header): trigger_id | button_label | response_text
Row 2: pricing_1 | Berapa Harga? | Harga kami mulai dari Rp 50.000...
Row 3: ship_1 | Pengiriman? | Pengiriman 1-3 hari ke seluruh Indonesia
... tambah FAQ sesuai kebutuhan

5. Add sheet baru: "Leads"
Row 1 (Header): timestamp | discord_tag | name | order_id | issue_type | status

6. Add sheet baru: "Analytics"
Row 1 (Header): date | total_tickets | unresolved_queries

7. Copy URL untuk dapatkan Sheet ID:
https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
Copy SHEET_ID ke .env
"""

# ============================================================================
# STEP 5: CREATE DISCORD BOT
# ============================================================================

"""
1. Buka https://discord.com/developers/applications
2. Click "New Application"
3. Masukkan nama (misal: "CS Bot")
4. Click "Create"
5. Go to "Bot" tab
6. Click "Add Bot"
7. Di TOKEN section, click "Copy"
8. Paste ke .env sebagai DISCORD_TOKEN:
   DISCORD_TOKEN=your_token_here

9. Enable required intents:
   - Scroll ke "Privileged Gateway Intents"
   - Enable: Message Content Intent
   - Enable: Members Intent
   - Click "Save Changes"

10. Dapatkan Bot ID:
    - Dari URL saat buka bot settings
    - Format: https://discord.com/developers/applications/{BOT_ID}
    
11. Generate invite link:
    https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions=8&scope=bot
    
    Replace {BOT_ID} dengan ID dari step 10

12. Buka link di browser, select server, click "Authorize"
"""

# ============================================================================
# STEP 6: SETUP DISCORD SERVER
# ============================================================================

"""
1. Di Discord server Anda:
   - Klik "+ Create Channel"
   - Buat 3 channel baru:
     * #support (untuk user request)
     * #staff-notifications (untuk notify tim)
     * #bot-logs (untuk bot logs)

2. Dapatkan Channel IDs (enable Developer Mode):
   - User Settings → Advanced → Toggle "Developer Mode"
   - Right-click channel → Copy Channel ID
   
3. Update .env:
   SUPPORT_CHANNEL_ID=123456789
   STAFF_NOTIFICATION_CHANNEL_ID=123456789
   LOGS_CHANNEL_ID=123456789

4. Set Bot Permissions (untuk each channel):
   - Right-click channel → Edit channel → Permissions
   - Find bot role
   - Enable: Send Messages, Create Threads, Manage Threads, Embed Links
"""

# ============================================================================
# STEP 7: SETUP .env FILE
# ============================================================================

"""
1. Di project folder, buat file .env (copy dari .env.example):
   copy .env.example .env

2. Edit .env dengan text editor (Notepad++, VS Code, dll):

   # Discord Configuration
   DISCORD_TOKEN=your_bot_token
   DISCORD_GUILD_ID=your_guild_id
   PREFIX=!

   # Google Sheets Configuration
   GOOGLE_SHEETS_ID=your_sheet_id
   CREDENTIALS_FILE=credentials.json

   # Channel Configuration
   SUPPORT_CHANNEL_ID=123456789
   STAFF_NOTIFICATION_CHANNEL_ID=123456789
   LOGS_CHANNEL_ID=123456789

   # Bot Configuration
   LOG_LEVEL=INFO
   DEBUG_MODE=False

3. Save file
4. Verify file ada di C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot\.env
"""

# ============================================================================
# STEP 8: VERIFY SETUP
# ============================================================================

"""
Pre-flight checklist:

□ Python 3.10+ installed
□ requirements.txt installed
□ credentials.json di project root
□ Google Sheets created dengan 3 tab (FAQ, Leads, Analytics)
□ Google Sheets shared ke service account email
□ Discord bot created dan added to server
□ .env file created dengan semua config
□ All Channel IDs di .env correct
□ All permissions set di Discord channels

Jika semua sudah, lanjut ke step berikutnya.
"""

# ============================================================================
# STEP 9: RUN BOT FOR FIRST TIME
# ============================================================================

"""
1. Open Command Prompt / PowerShell

2. Navigate to project:
   cd C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot

3. Run bot:
   python main.py

4. Expected output:
   ══════════════════════════════════════════════
   🤖 Initializing Discord Customer Support Bot
   ══════════════════════════════════════════════
   📊 Connecting to Google Sheets...
   ✅ Database connected successfully
   📦 Loading cogs...
   ✅ Loaded cog: commands
   ✅ Loaded cog: events
   🚀 Starting bot...
   ✅ Bot logged in as YourBotName#1234
   ✅ Bot is in 1 server(s)

5. Bot is now RUNNING!
"""

# ============================================================================
# STEP 10: TEST BOT FUNCTIONALITY
# ============================================================================

"""
1. Di Discord server, try commands:
   - !support
     Expected: Menu muncul dengan 3 buttons
   
   - !faq
     Expected: Daftar FAQ muncul
   
   - !stats
     Expected: Statistik ditampilkan (admin only)

2. Test button:
   - Click "Hubungi Support"
   - Expected: Modal form muncul
   - Fill form dan submit
   - Expected: Confirmation message dan staff notification

3. Check logs:
   - Buka folder: logs/
   - File bot_YYYY-MM-DD.log sudah exist
   - Lihat entries untuk verify operation

4. Check Google Sheets:
   - Buka Tab "Leads"
   - Dari ticket test, row baru harus muncul
"""

# ============================================================================
# STEP 11: KEEPING BOT RUNNING
# ============================================================================

"""
Options untuk keep bot running 24/7:

OPTION 1: Development (Selama ngoding)
- Jalankan di terminal
- python main.py
- Bot running selama terminal terbuka
- STOP dengan: Ctrl+C

OPTION 2: Windows Service (Advanced)
- Setup bot sebagai Windows service
- Requires: NSSM (Non-Sucking Service Manager)
- Follow guide online

OPTION 3: Cloud Hosting (Recommended Production)
Option A - Railway.app
  1. Create account di https://railway.app
  2. Connect GitHub repository
  3. Add environment variables di dashboard
  4. Auto-deploy when push to main branch
  5. Free tier available
  
Option B - Render.com
  1. Create account di https://render.com
  2. New → Web Service
  3. Connect GitHub
  4. Set start command: python main.py
  5. Free tier available
  
Option C - DigitalOcean VPS ($5/month)
  1. Create Ubuntu droplet
  2. SSH into server
  3. Install Python & dependencies
  4. Setup systemd service untuk auto-restart
  5. Use tmux or screen untuk background process
"""

# ============================================================================
# STEP 12: DAILY OPERATIONS
# ============================================================================

"""
Checklist harian:

Morning:
□ Verify bot still running: ping bot di Discord
□ Check logs untuk errors
□ Clear old logs (optional)

During day:
□ Monitor support tickets
□ Respond to staff notifications
□ Update FAQ jika ada pertanyaan recurring

End of day:
□ Check stats: !stats command
□ Backup important data (export from Google Sheets)
□ Review logs untuk issues

Weekly:
□ Review analytics
□ Archive resolved tickets
□ Update FAQ dengan trending issues
□ Restart bot (maintenance)

Monthly:
□ Clean up old logs
□ Review performance metrics
□ Plan improvements
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
Setelah bot running:

1. Customize FAQ
   - Edit Google Sheets Tab "FAQ"
   - Add/remove questions sesuai bisnis Anda
   - !reload untuk update di bot

2. Train staff
   - Show how to take tickets
   - Show how to respond
   - Show how to check stats

3. Promote to users
   - Share bot availability
   - Tell people about !support command

4. Monitor & improve
   - Watch tickets patterns
   - Improve response time
   - Add new features as needed

5. Explore advanced features
   - Check ADVANCED_FEATURES.md
   - Implement rating system
   - Add priority levels
   - Setup analytics

Enjoy! 🎉
"""
