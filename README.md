# Discord Customer Support Bot 🤖

Complete framework for building a Discord Customer Support Bot integrated with Google Sheets using Python.

## 🎨 CLI Control Panel

Interactive command-line interface for easy bot management with colored output and clean menus.

**Launch the CLI:**
```bash
python cli_app.py
```

**CLI Features:**
- 🎛️ **Start/Stop Bot** - Dynamic menu based on bot status
- ⚙️ **Admin Role Settings** - Configure which roles have admin permissions
- 📝 **FAQ Management** - Add/delete FAQs with multi-line support (ESC to finish)
- 🔄 **Database Refresh** - Reload changes instantly
- 📊 **View Logs** - Monitor bot activity with color-coded messages
- 📈 **Bot Statistics** - See detailed connection status and server info

## 📋 Key Features

- ✅ **Interactive Support Menu** - User-friendly buttons and modals
- ✅ **Google Sheets Integration** - Admin-manageable database
- ✅ **FAQ Management** - Manage FAQs without coding
- ✅ **Ticket System** - Escalation system with Private Threads
- ✅ **Staff Notifications** - Real-time notifications to support team
- ✅ **Analytics** - Track support performance
- ✅ **Logging System** - Complete audit trail of all activities
- ✅ **CLI Control Panel** - Interactive command-line interface

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud Account (for Google Sheets API)
- Discord Server & Bot Token

### Installation

```bash
# 1. Clone repository
git clone https://github.com/7FIl/CS_Bot.git
cd CS_Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env with your credentials

# 4. Run bot
# Option A: Use CLI (Recommended)
python cli_app.py

# Option B: Use command line
python main.py
```

### 📖 Detailed Setup Guide

**New to setting this up?** Follow our comprehensive guide:

👉 **[See SETUP.md for complete installation instructions](SETUP.md)**

The setup guide includes:
- Google Sheets API configuration
- Discord bot creation and permissions
- Service account setup
- Environment variables configuration
- Testing and troubleshooting

## 📁 Project Structure

```
CS_Bot/
├── main.py                 # Bot entry point
├── config.py              # Main configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Template environment variables
├── SETUP.md              # Complete setup guide
├── README.md             # This file
│
├── handlers/
│   ├── database.py       # Google Sheets manager
│   ├── commands.py       # All discord commands
│   ├── modals.py         # Form modal & ticket system
│   └── events.py         # Discord event handlers
│
├── utils/
│   └── logger.py         # Logging system
│
├── logs/                 # Log files (auto-created)
│   └── bot_YYYY-MM-DD.log
│
└── data/                 # Data files (auto-created)
```

## 💻 Commands

| Command | Description | Permission |
|---------|-------------|-----------|
| `!support` | Open main support menu | All users |
| `!faq` | Display FAQ list | All users |
| `!reload` | Reload data from Google Sheets | Admin |
| `!stats` | Display support statistics | Admin |

## 🔧 Google Sheets Structure

### Tab 1: FAQ
Manage frequently asked questions

| trigger_id | button_label | response_text |
|-----------|--------------|---------------|
| pricing_1 | What's the price? | Our prices start from $50... |
| ship_1 | Shipping info? | We ship nationwide... |

### Tab 2: Leads
Customer ticket database (auto-populated by bot)

| timestamp | discord_tag | name | order_id | issue_type | status |
|-----------|------------|------|----------|-----------|--------|
| 2024-12-18 10:30 | User#1234 | John | #12345 | Item Not Arrived | PENDING |

### Tab 3: Analytics
Support performance data (auto-logged by bot)

| date | total_tickets | unresolved_queries |
|------|---------------|------------------|
| 2024-12-18 | 15 | 3 |

## 🔐 Security

- ✅ Use environment variables for all secrets
- ✅ Secure service account credentials
- ✅ Built-in rate limiting
- ✅ Audit trail for all activities

## 📊 Workflow

### User Flow
```
1. User types !support or clicks support button
2. Menu appears with 3 options: FAQ, Chat, Status
3. User selects "Contact Support"
4. Modal form appears for data entry
5. Data is saved to Google Sheets
6. Staff is notified via notification channel
7. Staff takes ticket → Private thread is created
8. Conversation occurs in private thread
9. Staff closes ticket → Status updated
```

### Admin Flow
```
1. Admin opens Google Sheets FAQ tab
2. Edit/add FAQ without coding
3. In Discord, admin types !reload
4. FAQ is updated in bot
5. Users can view new FAQ via !faq
```

## 📈 Scalability

- Supports unlimited FAQ items
- Handles concurrent support requests
- Automatic daily log rotation
- Efficient Google Sheets caching
- Minimal API calls with smart caching

## 🐛 Troubleshooting

### Common Issues

- **Bot not responding** → Check `.env` configuration and bot permissions
- **Google Sheets error** → Verify `credentials.json` and sheet sharing
- **Modal not appearing** → Update discord.py: `pip install -U discord.py`

For detailed troubleshooting steps, see [SETUP.md](SETUP.md#6️⃣-troubleshooting)

## 📝 Logging

All activities are logged in `logs/` folder:
- Daily log files: `bot_YYYY-MM-DD.log`
- Separate loggers for Database, Events, Bot
- Console output + File output

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - Feel free to use for personal or commercial projects

## 📧 Support

For setup help and detailed documentation:
- 📖 [Complete Setup Guide](SETUP.md)
- 📂 Check logs in `logs/` folder
- 💻 Review code in `handlers/` folder

---


*Built in python using discord.py and gspread*
