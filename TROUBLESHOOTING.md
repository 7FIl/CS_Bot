"""
Troubleshooting Guide
Panduan troubleshooting masalah umum
"""

# ============================================================================
# COMMON ISSUES & SOLUTIONS
# ============================================================================

"""
ISSUE 1: "ModuleNotFoundError: No module named 'discord'"
───────────────────────────────────────────────────────
SOLUTION:
pip install -r requirements.txt

Atau jika masih error:
pip install --upgrade discord.py==2.3.2


ISSUE 2: "credentials.json not found"
───────────────────────────────────────
SOLUTION:
1. Pastikan file credentials.json ada di folder project root
2. Path should be: C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot\credentials.json
3. Jika belum punya, follow SETUP_GUIDE.md untuk download dari Google Cloud Console


ISSUE 3: "Failed to open spreadsheet"
──────────────────────────────────────
SOLUTION:
1. Cek GOOGLE_SHEETS_ID di .env, pastikan correct
2. Cek Google Sheets sudah di-share ke email Service Account
3. Cek tiga tabs ada: FAQ, Leads, Analytics
4. Header row harus ada di baris pertama setiap tab

Untuk verify:
- Buka https://sheets.google.com
- Find spreadsheet by URL
- Share dengan email dari credentials.json
- Give "Editor" permission


ISSUE 4: "Bot tidak merespons command"
──────────────────────────────────────
SOLUTION:
1. Cek DISCORD_TOKEN di .env valid
   - Buka https://discord.com/developers/applications
   - Klik aplikasi Anda
   - Tab "Bot" → copy token baru
   - Update .env

2. Cek bot sudah di-invite ke server
   - Generate URL: https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot
   - Replace YOUR_BOT_ID dari Developer Portal
   - Klik link untuk invite

3. Cek Message Content Intent enabled
   - https://discord.com/developers/applications
   - Klik bot
   - Tab "Bot"
   - Scroll ke "Privileged Gateway Intents"
   - Enable "Message Content Intent"
   - Klik "Save"

4. Check logs
   - Lihat file di folder logs/
   - Search untuk error messages


ISSUE 5: "Modal tidak muncul"
──────────────────────────────
SOLUTION:
- Update discord.py ke versi terbaru:
  pip install -U discord.py

- Cek button style dan custom_id valid:
  - Label maksimal 80 karakter
  - custom_id maksimal 100 karakter
  - custom_id harus unique


ISSUE 6: "Google Sheets API rate limit exceeded"
──────────────────────────────────────────────────
SOLUTION:
1. Bot sudah implement caching, tapi jika masih kena limit:
2. Add delay antar request:
   import time
   time.sleep(0.1)  # 100ms delay

3. Batch operations jika bisa
4. Request quote increase di Google Cloud Console


ISSUE 7: "Private Thread tidak terbuat"
────────────────────────────────────────
SOLUTION:
1. Cek channel permissions
   - Bot harus punya "Manage Threads" permission
   
2. Verify di Discord Server:
   - Right-click channel
   - Edit channel → Permissions
   - Find bot role
   - Enable "Create Public Threads" dan "Manage Threads"

3. Thread hanya bisa dibuat di text channels, bukan category


ISSUE 8: "Notification tidak masuk ke staff channel"
─────────────────────────────────────────────────────
SOLUTION:
1. Cek STAFF_NOTIFICATION_CHANNEL_ID di .env correct
   - Right-click channel di Discord
   - Copy Channel ID
   - Paste ke .env

2. Cek bot punya akses ke channel
   - Right-click channel → Permissions
   - Cek bot punya "Send Messages" dan "Embed Links"

3. Cek channel exists
   - Jika channel didelete, buat baru dan update .env


ISSUE 9: "Database append_row returns error"
──────────────────────────────────────────────
SOLUTION:
1. Cek tab name di .env match Google Sheets
   - FAQ_TAB_NAME=FAQ (harus persis)
   - LEADS_TAB_NAME=Leads
   - ANALYTICS_TAB_NAME=Analytics

2. Cek header row ada di sheet
   - Row 1 harus berisi column names
   - Jangan ada row kosong di tengah

3. Cek Google Sheets share permission
   - Harus "Editor" permission
   - Bukan "Viewer" atau "Commenter"


ISSUE 10: ".env file not loading"
──────────────────────────────────
SOLUTION:
1. Pastikan file bernama ".env" (bukan .env.txt atau .envexample)
   - Windows: Gunakan terminal untuk create
   - copy .env.example .env

2. .env harus di folder root project
   - C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot\.env

3. Format harus benar, tanpa quotes
   - WRONG: DISCORD_TOKEN="abc123def456"
   - RIGHT: DISCORD_TOKEN=abc123def456

4. Restart bot setelah update .env
   - kill python process
   - Jalankan main.py lagi
"""

# ============================================================================
# DEBUG MODE
# ============================================================================

"""
Enable DEBUG_MODE di .env untuk lebih verbose logging:

DEBUG_MODE=True

Ini akan:
- Print semua command di console
- Show interaction details
- More detailed error messages
- Extra logging di log files

Jangan enable di production karena performance impact.
"""

# ============================================================================
# CHECKING LOGS
# ============================================================================

"""
Log files ada di folder: logs/

Setiap hari ada file baru: bot_YYYY-MM-DD.log

Untuk check error:
1. Buka file log terbaru
2. Search untuk "ERROR" keyword
3. Lihat context dan timestamp

Important log lines:
- "[ERROR]" = Serious problem
- "[WARNING]" = Something unusual
- "[INFO]" = Normal operation info

Contoh debug session:
1. Start bot: python main.py
2. Open logs/bot_2024-12-18.log
3. Watch log real-time sambil test command
4. Lihat error details jika ada
"""

# ============================================================================
# DATABASE HEALTH CHECK
# ============================================================================

"""
Script untuk verify Google Sheets connection:

from handlers.database import get_db_manager

try:
    db = get_db_manager()
    
    # Test read
    faq = db.get_faq_data()
    print(f"✅ Can read FAQ: {len(faq)} records")
    
    # Test write
    db.save_lead("Test#1234", "Test User", "#TEST", "Test", "PENDING")
    print("✅ Can write to Leads")
    
    print("✅ Database connection OK")
except Exception as e:
    print(f"❌ Database error: {str(e)}")
"""

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

"""
Monitor bot performance:

Dalam log files, lihat:
1. Database query time
   - "Database query took X ms"
   
2. Message processing time
   - Harus < 1 second

3. API response time
   - Harus < 2 seconds

Jika lambat:
1. Check logs untuk ERROR messages
2. Check network connection
3. Check Google Sheets tidak terlalu banyak data
4. Check server tidak overloaded (check CPU usage)

Optimization tips:
1. Archive old leads ke sheet terpisah jika > 10,000 rows
2. Clear logs older than 30 days
3. Restart bot setiap minggu untuk memory cleanup
"""

# ============================================================================
# GETTING HELP
# ============================================================================

"""
Jika masih stuck:

1. Check README.md
   - Copy paste title issue ke search
   
2. Check SETUP_GUIDE.md
   - Verifikasi semua step sudah dilakukan

3. Check log files
   - Lihat error message detail
   
4. Isolate problem
   - Test connection ke Google Sheets manually
   - Test bot command di DM
   - Test button di public channel
   
5. Recreate minimal example
   - Create simple test script
   - Identify which part failing

6. Share logs + error
   - Screenshot error message
   - Share relevant log lines
   - Describe what you tried
"""
