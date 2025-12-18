"""
Google Sheets Setup Guide for Discord Customer Support Bot

Panduan lengkap untuk setup Google Sheets API dan struktur database.
"""

# ============================================================================
# STEP 1: Google Cloud Console Setup
# ============================================================================

"""
1. Buka https://console.cloud.google.com
2. Buat project baru:
   - Klik "Select a Project" di top
   - Klik "New Project"
   - Masukkan nama project (misal: "Discord CS Bot")
   - Klik "Create"

3. Enable Google Sheets API:
   - Di search bar, ketik "Google Sheets API"
   - Klik "Google Sheets API"
   - Klik "Enable"

4. Enable Google Drive API:
   - Di search bar, ketik "Google Drive API"
   - Klik "Google Drive API"
   - Klik "Enable"

5. Create Service Account:
   - Di sidebar, pilih "Credentials"
   - Klik "Create Credentials" → "Service Account"
   - Isi form:
     * Service account name: "Discord Bot"
     * Service account description: "For Discord Customer Support Bot"
   - Klik "Create and Continue"
   - Di step 2 dan 3, biarkan kosong dan klik "Continue"
   - Klik "Done"

6. Buat Key:
   - Di Credentials page, cari Service Account yang baru dibuat
   - Klik email-nya
   - Tab "Keys" → "Add Key" → "Create new key"
   - Pilih "JSON"
   - Klik "Create"
   - File akan otomatis download → simpan sebagai "credentials.json"
   - Pindahkan file ini ke folder project root (CS_Bot/)

7. Share Google Sheets dengan Service Account:
   - Di file credentials.json, cari "client_email"
   - Copy email tersebut (format: bot-cs@project.iam.gserviceaccount.com)
   - Buka Google Sheets Anda
   - Klik "Share" (top right)
   - Paste email tersebut dan give access "Editor"
   - Uncheck "Notify people"
   - Klik "Share"

8. Copy Sheet ID:
   - Dari URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   - Copy SHEET_ID ke .env file sebagai GOOGLE_SHEETS_ID
"""

# ============================================================================
# STEP 2: Google Sheets Structure
# ============================================================================

"""
Buat satu file Google Spreadsheet dengan 3 Tab berikut:

TAB 1: "FAQ"
═══════════════════════════════════════════════════════════════

Kolom:
- A: trigger_id      (ID unik untuk trigger, misal: "pricing_1")
- B: button_label    (Label tombol, misal: "Berapa Harga?")
- C: response_text   (Jawaban lengkap)

Contoh Data:
├─ Row 1 (Header): trigger_id | button_label | response_text
├─ Row 2: pricing_1 | Berapa Harga? | Harga kami mulai dari Rp 50.000...
├─ Row 3: shipping_1 | Berapa Lama Pengiriman? | Pengiriman 1-3 hari...
├─ Row 4: return_1 | Kebijakan Retur? | Kami menerima retur dalam 30 hari...
└─ ... (tambahkan FAQ sesuai kebutuhan)


TAB 2: "Leads"
═══════════════════════════════════════════════════════════════

Kolom:
- A: timestamp       (Waktu ticket dibuat)
- B: discord_tag     (Discord tag user)
- C: name            (Nama user)
- D: order_id        (Nomor order/invoice)
- E: issue_type      (Tipe masalah)
- F: status          (Status: PENDING, IN_PROGRESS, RESOLVED)

Contoh Data:
├─ Row 1 (Header): timestamp | discord_tag | name | order_id | issue_type | status
├─ Row 2: 2024-12-18 10:30:45 | Budi#1234 | Budi Santoso | #12345 | Barang Belum Sampai | PENDING
└─ ... (auto-populated oleh bot saat user submit form)


TAB 3: "Analytics"
═══════════════════════════════════════════════════════════════

Kolom:
- A: date                (Tanggal)
- B: total_tickets       (Total ticket hari itu)
- C: unresolved_queries  (Query yang belum selesai)

Contoh Data:
├─ Row 1 (Header): date | total_tickets | unresolved_queries
├─ Row 2: 2024-12-18 | 15 | 3
└─ ... (auto-logged oleh bot)
"""

# ============================================================================
# STEP 3: .env Configuration
# ============================================================================

"""
Copy file .env.example menjadi .env dan isi dengan:

DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_GUILD_ID=123456789

GOOGLE_SHEETS_ID=your_sheet_id_here
CREDENTIALS_FILE=credentials.json

SUPPORT_CHANNEL_ID=123456789
STAFF_NOTIFICATION_CHANNEL_ID=123456789
LOGS_CHANNEL_ID=123456789

PREFIX=!
LOG_LEVEL=INFO
DEBUG_MODE=False

FAQ_TAB_NAME=FAQ
LEADS_TAB_NAME=Leads
ANALYTICS_TAB_NAME=Analytics
"""

# ============================================================================
# STEP 4: Discord Server Setup
# ============================================================================

"""
1. Buat Discord Server atau gunakan server yang sudah ada

2. Buat Channels berikut:
   ├─ #support (untuk user request bantuan)
   ├─ #staff-notifications (untuk notifikasi ticket ke staff)
   └─ #bot-logs (untuk logging activity)

3. Dapatkan Channel IDs:
   - Enable Developer Mode (User Settings → Advanced → Developer Mode)
   - Right-click channel → Copy Channel ID
   - Paste ke .env file

4. Invite Bot ke Server:
   - https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot
   - Replace YOUR_BOT_ID dengan bot ID dari Developer Portal
   - Pilih server
   - Klik Authorize

5. Give Bot Permissions:
   - Role bot should have: Send Messages, Create Public Threads, Manage Messages, Embed Links
"""

# ============================================================================
# STEP 5: Discord Bot Token Setup
# ============================================================================

"""
1. Buka https://discord.com/developers/applications

2. Create New Application:
   - Klik "New Application"
   - Masukkan nama (misal: "CS Bot")
   - Klik "Create"

3. Dapatkan Bot Token:
   - Di sidebar, pilih "Bot"
   - Klik "Add Bot"
   - Di section TOKEN, klik "Copy"
   - Paste ke .env sebagai DISCORD_TOKEN

4. Enable Required Intents:
   - Scroll ke "Privileged Gateway Intents"
   - Enable:
     * Message Content Intent
     * Members Intent
   - Klik "Save Changes"
"""

# ============================================================================
# IMPORTANT NOTES
# ============================================================================

"""
✅ CHECKLIST SEBELUM JALANKAN BOT:

□ credentials.json sudah didownload dan di-paste ke folder project
□ Google Sheets sudah di-share ke email Service Account
□ .env file sudah dibuat dengan semua konfigurasi
□ Discord Bot Token sudah di-copy ke DISCORD_TOKEN
□ Discord Channel IDs sudah diisi dengan benar
□ Google Sheets ID sudah diisi
□ Bot sudah di-invite ke Discord Server
□ Bot sudah diberi permission yang sesuai

⚠️ TROUBLESHOOTING:

Problem: "credentials.json not found"
→ Pastikan file credentials.json ada di folder root project

Problem: "Failed to open spreadsheet"
→ Pastikan Sheet sudah di-share ke email Service Account
→ Copy-paste URL sheet ke browser dan cek aksesnya

Problem: "Bot tidak merespons command"
→ Cek apakah TOKEN sudah benar di .env
→ Cek apakah bot sudah di-invite ke server
→ Cek apakah Message Content Intent sudah enabled

Problem: "Modal/Button tidak muncul"
→ Update discord.py ke versi terbaru: pip install -U discord.py
"""
