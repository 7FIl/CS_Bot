╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                 🚀 QUICK START GUIDE - 5 STEPS TO RUN 🚀                ║
║                                                                          ║
║            Discord Customer Support Bot dengan Google Sheets             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝


📋 STEP 1: INSTALL DEPENDENCIES (5 MINUTES)
══════════════════════════════════════════════════════════════════════════

1.1 Open Command Prompt or PowerShell
    ├─ Windows: Start Menu → Search "Command Prompt"
    └─ Or: Right-click → Terminal

1.2 Navigate to project folder
    cd C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot

1.3 Verify Python installed
    python --version
    ✓ Harus 3.10 atau lebih tinggi

1.4 Install all dependencies
    pip install -r requirements.txt
    ✓ Ini menginstall: discord.py, gspread, pandas, dll

1.5 Wait until complete
    ✓ Anda akan lihat: Successfully installed...


📊 STEP 2: SETUP GOOGLE SHEETS (15 MINUTES)
══════════════════════════════════════════════════════════════════════════

2.1 Open Google Cloud Console
    ✓ URL: https://console.cloud.google.com
    ✓ Login dengan Google account Anda

2.2 Create new project
    ├─ Click "Select a Project" (top)
    ├─ Click "New Project"
    ├─ Type name: "Discord CS Bot"
    └─ Click "Create"

2.3 Enable APIs
    ├─ Search bar → "Google Sheets API"
    ├─ Click "Enable"
    ├─ Search bar → "Google Drive API"
    └─ Click "Enable"

2.4 Create Service Account
    ├─ Sidebar: "Credentials"
    ├─ Click "Create Credentials" → "Service Account"
    ├─ Name: "Discord Bot"
    ├─ Click "Create and Continue"
    ├─ Skip the rest (just click Continue/Done)
    └─ Done!

2.5 Download credentials.json
    ├─ Back to Credentials page
    ├─ Find your Service Account
    ├─ Click "Keys" tab
    ├─ "Add Key" → "Create new key"
    ├─ Choose "JSON"
    ├─ Click "Create"
    └─ ✓ File auto-download

2.6 Move credentials.json
    ├─ Downloaded file: C:\Users\ADMIN\Downloads\credentials.json
    ├─ Move to: C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot\credentials.json
    └─ ✓ NOW it's in project root

2.7 Create Google Sheets
    ├─ Open: https://sheets.google.com
    ├─ Create new spreadsheet
    ├─ Rename 1st sheet to "FAQ"
    ├─ Add 2 more sheets: "Leads", "Analytics"
    └─ ✓ Done!

2.8 Add headers to sheets
    
    FAQ Sheet (Row 1):
    ├─ A1: trigger_id
    ├─ B1: button_label
    └─ C1: response_text
    
    Leads Sheet (Row 1):
    ├─ A1: timestamp
    ├─ B1: discord_tag
    ├─ C1: name
    ├─ D1: order_id
    ├─ E1: issue_type
    └─ F1: status
    
    Analytics Sheet (Row 1):
    ├─ A1: date
    ├─ B1: total_tickets
    └─ C1: unresolved_queries

2.9 Get Sheet ID
    ├─ URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
    ├─ Copy: SHEET_ID part
    └─ ✓ Save for later

2.10 Share Sheets with Service Account
     ├─ Click "Share" (top right)
     ├─ Google Cloud Console → Service Account email
     ├─ Copy email: bot-cs@project.iam.gserviceaccount.com
     ├─ Paste to Share dialog
     ├─ Set to "Editor"
     ├─ Uncheck "Notify people"
     └─ Click "Share"


🤖 STEP 3: CREATE DISCORD BOT (10 MINUTES)
══════════════════════════════════════════════════════════════════════════

3.1 Open Discord Developer Portal
    ✓ URL: https://discord.com/developers/applications
    ✓ Login dengan Discord account

3.2 Create new application
    ├─ Click "New Application"
    ├─ Name: "CS Bot"
    ├─ Accept terms
    └─ Click "Create"

3.3 Add Bot user
    ├─ Left menu: "Bot"
    ├─ Click "Add Bot"
    └─ ✓ Bot added!

3.4 Copy Bot Token
    ├─ TOKEN section: "Copy"
    ├─ Save somewhere (you'll need it soon)
    └─ ✓ Don't share this with anyone!

3.5 Enable Message Content Intent
    ├─ Scroll down: "Privileged Gateway Intents"
    ├─ Toggle: "Message Content Intent" (ON)
    ├─ Toggle: "Members Intent" (ON)
    └─ Click "Save"

3.6 Create Discord Server (jika belum punya)
    ├─ Discord app
    ├─ "+" button → Create new server
    ├─ Name: "Support Bot Test" (atau nama lain)
    └─ ✓ Created!

3.7 Create channels in Discord server
    ├─ Server settings → Channels
    ├─ Create: #support
    ├─ Create: #staff-notifications
    ├─ Create: #bot-logs
    └─ ✓ Done!

3.8 Get Channel IDs
    ├─ Enable Developer Mode (User Settings → Advanced → Developer Mode)
    ├─ Right-click #support → "Copy Channel ID"
    ├─ Write down: SUPPORT_CHANNEL_ID
    ├─ Repeat untuk #staff-notifications
    ├─ Repeat untuk #bot-logs
    └─ ✓ You have 3 channel IDs

3.9 Get Server ID
    ├─ Right-click server name
    ├─ "Copy Server ID"
    └─ ✓ Write down: GUILD_ID

3.10 Get Bot ID
     ├─ URL path: https://discord.com/developers/applications/{BOT_ID}
     ├─ Copy BOT_ID from URL
     └─ ✓ Write down for invite link

3.11 Generate Invite Link
     ├─ URL: https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions=8&scope=bot
     ├─ Replace {BOT_ID}
     ├─ Open link in browser
     ├─ Select server from dropdown
     └─ Click "Authorize"

3.12 Verify bot in Discord
     ├─ Open Discord server
     ├─ Bot should appear in member list (online)
     └─ ✓ Success!


⚙️ STEP 4: CONFIGURE BOT (5 MINUTES)
══════════════════════════════════════════════════════════════════════════

4.1 Copy .env.example to .env
    ├─ Command: copy .env.example .env
    └─ ✓ Now you have .env file

4.2 Edit .env file
    ├─ Open in text editor (Notepad++, VS Code, etc)
    ├─ Fill in values:
    │
    │  DISCORD_TOKEN=<your_bot_token>
    │  DISCORD_GUILD_ID=<your_guild_id>
    │  PREFIX=!
    │
    │  GOOGLE_SHEETS_ID=<your_sheet_id>
    │  CREDENTIALS_FILE=credentials.json
    │
    │  SUPPORT_CHANNEL_ID=<support_channel_id>
    │  STAFF_NOTIFICATION_CHANNEL_ID=<staff_channel_id>
    │  LOGS_CHANNEL_ID=<logs_channel_id>
    │
    │  LOG_LEVEL=INFO
    │  DEBUG_MODE=False
    │
    └─ ✓ Save file

4.3 Verify .env is complete
    ✓ All values filled
    ✓ No empty values
    ✓ No quotes around values
    ✓ File is named ".env" (not .env.txt)


🚀 STEP 5: RUN BOT (2 MINUTES)
══════════════════════════════════════════════════════════════════════════

5.1 Open Command Prompt/PowerShell
    cd C:\Users\ADMIN\Desktop\P_Code\Python\CS_Bot

5.2 Run bot
    python main.py

5.3 Wait for startup messages
    Expected output:
    ├─ ==================================================
    ├─ 🤖 Initializing Discord Customer Support Bot
    ├─ ==================================================
    ├─ 📊 Connecting to Google Sheets...
    ├─ ✅ Database connected successfully
    ├─ 📦 Loading cogs...
    ├─ ✅ Loaded cog: commands
    ├─ ✅ Loaded cog: events
    ├─ 🚀 Starting bot...
    ├─ ✅ Bot logged in as CS Bot#xxxx
    └─ ✅ Bot is in 1 server(s)

5.4 Bot is RUNNING! 🎉
    ✓ Leave this terminal open
    ✓ Bot stays running while terminal is open
    ✓ Press Ctrl+C to stop

5.5 Test in Discord
    ├─ Go to Discord server
    ├─ Type: !support
    ├─ Expected: Menu with 3 buttons
    ├─ Type: !faq
    ├─ Expected: FAQ list appears
    └─ ✓ SUCCESS!


✅ VERIFICATION CHECKLIST
══════════════════════════════════════════════════════════════════════════

□ Python 3.10+ installed
□ Dependencies installed (pip install -r requirements.txt)
□ credentials.json di project root
□ Google Sheets created dengan 3 tabs
□ Google Sheets shared ke Service Account
□ .env file created dan filled
□ Bot Token di .env
□ Channel IDs di .env
□ Guild ID di .env
□ Sheet ID di .env
□ Discord bot invited to server
□ Bot appears online in Discord
□ !support command works
□ Menu with buttons appears


🎯 NEXT STEPS AFTER RUNNING
══════════════════════════════════════════════════════════════════════════

Immediate (Minutes):
  ✓ Bot running = Success! 🎉
  ✓ Keep terminal open (bot stays online)

Short-term (Hours):
  ✓ Add FAQ items to Google Sheets
  ✓ Run !reload di Discord
  ✓ Test !faq command
  ✓ Test button clicks

Medium-term (Days):
  ✓ Train staff on system
  ✓ Configure staff roles
  ✓ Test full ticket flow
  ✓ Monitor logs

Long-term (Weeks):
  ✓ Deploy to production hosting
  ✓ Announce to users
  ✓ Gather feedback
  ✓ Optimize based on usage


💡 KEEPING BOT RUNNING 24/7
══════════════════════════════════════════════════════════════════════════

Option 1: Development Mode (while you work)
  └─ python main.py
     (Bot runs while terminal is open)

Option 2: Keep Window Open
  └─ Minimize window, leave running
     (Windows: Alt+Tab to switch between)

Option 3: Production Hosting
  └─ Deploy to Railway.app or Render.com
     (Recommended for always-on)

Option 4: Windows Task Scheduler
  └─ Advanced, can set bot to auto-start
     (Requires Python setup on system PATH)


🐛 TROUBLESHOOTING DURING SETUP
══════════════════════════════════════════════════════════════════════════

Problem: "Python not recognized"
→ Install Python, add to PATH, restart terminal

Problem: "ModuleNotFoundError: No module named 'discord'"
→ Run: pip install -r requirements.txt

Problem: "credentials.json not found"
→ Download from Google Cloud, move to project root

Problem: "Bot won't login"
→ Check TOKEN in .env
→ Check token is current (not old)

Problem: "!support command doesn't work"
→ Ensure Message Content Intent enabled
→ Check prefix in .env (default: !)
→ Restart bot after changes

Problem: "Modal doesn't appear"
→ Update discord.py: pip install -U discord.py

Problem: "Google Sheets error"
→ Check Sheet shared to Service Account
→ Check tab names match config.py
→ Check headers in row 1


📚 HELPFUL DOCUMENTS
══════════════════════════════════════════════════════════════════════════

Getting Started:
  → README.md - Full overview
  → DOCUMENTATION_INDEX.md - Find right doc

Having Issues:
  → TROUBLESHOOTING.md - Common problems
  → logs/bot_YYYY-MM-DD.log - Error details

Want to Customize:
  → CUSTOMIZATION_TEMPLATES.md - Code examples
  → ADVANCED_FEATURES.md - New features
  → API_REFERENCE.md - All methods

Need Details:
  → INSTALLATION.md - Complete steps
  → SETUP_GUIDE.md - Configuration guide
  → PROJECT_SUMMARY.md - Architecture


════════════════════════════════════════════════════════════════════════════

                    YOU'RE READY! 🚀

Now follow the 5 steps above and your bot will be running!

If you get stuck, check the troubleshooting section or read the docs.

Good luck! 💻✨

════════════════════════════════════════════════════════════════════════════
