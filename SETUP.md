# Setup Guide - Discord Customer Support Bot

This guide will walk you through setting up the Discord Customer Support Bot from scratch.

## 📋 Prerequisites

- Python 3.10 or higher
- Google Account
- Discord Account
- Text editor (VS Code recommended)

---

## 1️⃣ Google Sheets API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "Discord Support Bot")
4. Click **"Create"**

### Step 2: Enable Google Sheets API

1. In Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Sheets API"**
3. Click on it and press **"Enable"**
4. Also search and enable **"Google Drive API"**

### Step 3: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in:
   - **Service account name**: `discord-bot-service`
   - **Service account ID**: (auto-generated)
   - **Description**: "Service account for Discord support bot"
4. Click **"Create and Continue"**
5. Skip optional steps, click **"Done"**

### Step 4: Create & Download Credentials

1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **"JSON"** format
5. Click **"Create"**
6. A JSON file will download automatically
7. **Rename this file to `credentials.json`**
8. **Move it to your bot's root directory** (`CS_Bot/`)

### Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a **new blank spreadsheet**
3. Name it: **"Discord Support Bot Database"**
4. Create **3 tabs** (sheets) with these exact names:
   - `FAQ`
   - `Leads`
   - `Analytics`

### Step 6: Configure Sheet Structure

**FAQ Tab Headers (Row 1):**
```
trigger_id | button_label | response_text
```

**Example FAQ data:**
```
pricing_1 | What's the price? | Our prices start from $50...
shipping_1 | Shipping info? | We ship nationwide within 3-5 business days...
```

**Leads Tab Headers (Row 1):**
```
timestamp | ticket_number | discord_tag | name | order_id | issue_type | status
```
*(This will be auto-populated by the bot)*

**Analytics Tab Headers (Row 1):**
```
date | total_tickets | unresolved_queries
```
*(This will be auto-populated by the bot)*

### Step 7: Share Sheet with Service Account

1. Open your Google Sheet
2. Click **"Share"** button (top right)
3. Open the `credentials.json` file you downloaded
4. Find the `"client_email"` field (looks like: `xxx@xxx.iam.gserviceaccount.com`)
5. Copy this email address
6. Paste it in the **"Share"** dialog
7. Give it **"Editor"** access
8. **UNCHECK** "Notify people"
9. Click **"Share"**

### Step 8: Get Spreadsheet ID

1. Look at your Google Sheet URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```
2. Copy the **SPREADSHEET_ID** part (long string between `/d/` and `/edit`)
3. Save this ID for the environment variables setup

---

## 2️⃣ Discord Bot Setup

### Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Enter name: **"Support Bot"**
4. Click **"Create"**

### Step 2: Create Bot User

1. In your application, go to **"Bot"** tab (left sidebar)
2. Click **"Add Bot"** → **"Yes, do it!"**
3. Under **"Privileged Gateway Intents"**, enable:
   - ✅ **Presence Intent**
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
4. Click **"Save Changes"**

### Step 3: Get Bot Token

1. Under **"Bot"** tab, find **"TOKEN"** section
2. Click **"Reset Token"** → **"Yes, do it!"**
3. Click **"Copy"** to copy your bot token
4. **⚠️ KEEP THIS SECRET! Never share it publicly!**
5. Save this token for environment variables setup

### Step 4: Get Bot Invite Link

1. Go to **"OAuth2"** → **"URL Generator"** tab
2. Under **"Scopes"**, select:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Under **"Bot Permissions"**, select:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Create Public Threads
   - ✅ Create Private Threads
   - ✅ Manage Threads
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis
4. Copy the generated URL at the bottom

### Step 5: Invite Bot to Your Server

1. Paste the URL from Step 4 into your browser
2. Select your Discord server
3. Click **"Authorize"**
4. Complete the CAPTCHA

### Step 6: Get Server & Channel IDs

**Enable Developer Mode:**
1. Open Discord → User Settings → Advanced
2. Enable **"Developer Mode"**

**Get Guild (Server) ID:**
1. Right-click your server icon
2. Click **"Copy Server ID"**
3. Save this for environment variables

**Create and Get Channel IDs:**
1. Create these channels in your Discord server:
   - `#support` - Where users interact with the bot
   - `#staff-notifications` - Where staff receive ticket alerts
   - `#logs` - Where bot logs are sent (optional)

2. Right-click each channel → **"Copy Channel ID"**
3. Save these IDs for environment variables

---

## 3️⃣ Bot Installation

### Step 1: Clone/Download Repository

```bash
cd C:\Users\ADMIN\Desktop\P_Code\Python
git clone <your-repo-url> CS_Bot
cd CS_Bot
```

Or download and extract the ZIP file.

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` file and fill in your values:

```env
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_server_id_here
PREFIX=!

# Google Sheets Configuration
GOOGLE_SHEETS_ID=your_spreadsheet_id_here
CREDENTIALS_FILE=credentials.json

# Channel IDs
SUPPORT_CHANNEL_ID=your_support_channel_id_here
STAFF_NOTIFICATION_CHANNEL_ID=your_staff_channel_id_here
LOGS_CHANNEL_ID=your_logs_channel_id_here

# Spreadsheet Tab Names (match your sheet exactly)
FAQ_TAB_NAME=FAQ
LEADS_TAB_NAME=Leads
ANALYTICS_TAB_NAME=Analytics

# Bot Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### Step 4: Verify Credentials File

Ensure `credentials.json` is in the root directory:
```
CS_Bot/
├── credentials.json  ← Should be here
├── .env
├── main.py
└── ...
```

---

## 4️⃣ Running the Bot

### Start the Bot

```bash
python main.py
```

### Expected Output

```
==================================================
🤖 Initializing Discord Customer Support Bot
==================================================
📊 Connecting to Google Sheets...
✅ Database connected successfully
📦 Loading cogs...
✅ Loaded cog: commands
✅ Loaded cog: events
✅ Loaded cog: modals
🚀 Starting bot...
✅ Bot logged in as SupportBot#1234
```

---

## 5️⃣ Testing the Bot

### Test Commands

In your Discord server, try these commands:

```
!support    - Open support menu
!faq        - View FAQ list
!stats      - View bot statistics (admin only)
!reload     - Reload data from Google Sheets (admin only)
```

### Test Support Flow

1. Type `!support` in `#support` channel
2. Click **"Contact Support"** button
3. Fill in the modal form
4. Submit
5. Check `#staff-notifications` for the alert
6. Staff can click **"Take Ticket"** to handle it

---

## 6️⃣ Troubleshooting

### Bot Won't Start

**Error: `Missing Token`**
- Check `.env` file has correct `DISCORD_TOKEN`
- Token should have no quotes or spaces

**Error: `Privileged intent not enabled`**
- Go to Discord Developer Portal → Bot → Enable all intents

### Google Sheets Connection Failed

**Error: `credentials.json not found`**
- Ensure file is in root directory
- Check filename is exactly `credentials.json`

**Error: `Permission denied`**
- Open Google Sheet → Share with service account email
- Give "Editor" access

**Error: `Spreadsheet not found`**
- Check `GOOGLE_SHEETS_ID` in `.env` is correct
- Verify sheet is accessible

### Bot Can't Send Messages

**Check bot has permissions:**
- Right-click bot in members list
- Ensure it has proper role with permissions
- Check channel-specific permissions

### Modal Won't Open

**Update discord.py:**
```bash
pip install -U discord.py
```

### Commands Not Working

**Check bot prefix:**
- Default is `!`
- Verify in `.env` file: `PREFIX=!`

---

## 7️⃣ Security Best Practices

### ⚠️ Never Commit Sensitive Files

Add to `.gitignore`:
```gitignore
.env
credentials.json
*.session
__pycache__/
logs/*.log
```

### 🔒 Keep Tokens Secret

- Never share `DISCORD_TOKEN`
- Never share `credentials.json`
- Never commit `.env` to Git
- Use `.env.example` as template only

### 🛡️ Secure Your Server

- Limit staff role permissions
- Use private threads for tickets
- Regularly review Google Sheets access
- Enable 2FA on Discord and Google accounts

---

## 8️⃣ Production Deployment

### Using a VPS/Cloud Server

1. **Recommended Services:**
   - DigitalOcean
   - AWS EC2
   - Google Cloud Compute
   - Heroku

2. **Setup Process:**
   ```bash
   # Install Python
   sudo apt update
   sudo apt install python3 python3-pip
   
   # Clone repository
   git clone <your-repo>
   cd CS_Bot
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Configure .env file
   nano .env
   
   # Run with screen (keeps running after logout)
   screen -S discord-bot
   python3 main.py
   # Press Ctrl+A then D to detach
   ```

3. **Auto-restart with systemd:**
   Create `/etc/systemd/system/discord-bot.service`:
   ```ini
   [Unit]
   Description=Discord Support Bot
   After=network.target
   
   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/path/to/CS_Bot
   ExecStart=/usr/bin/python3 /path/to/CS_Bot/main.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   ```

---

## 9️⃣ Maintenance

### Update FAQ

1. Open Google Sheets → FAQ tab
2. Add/edit rows
3. In Discord, run `!reload` command
4. Changes take effect immediately

### View Logs

```bash
# View today's log
tail -f logs/bot_YYYY-MM-DD.log

# Search for errors
grep ERROR logs/bot_YYYY-MM-DD.log
```

### Backup Data

Regularly export your Google Sheet:
- File → Download → CSV or Excel

---

## 🆘 Support

If you encounter issues not covered here:

1. Check the logs in `logs/` folder
2. Verify all IDs in `.env` are correct
3. Test internet connection to Discord and Google APIs
4. Review Discord bot permissions

---

## ✅ Setup Complete!

Your Discord Customer Support Bot is now ready to use! 🎉

**Quick Reference:**
- Commands: `!support`, `!faq`, `!stats`, `!reload`
- Edit FAQ: Google Sheets → FAQ tab
- View tickets: Google Sheets → Leads tab
- Check analytics: Google Sheets → Analytics tab
