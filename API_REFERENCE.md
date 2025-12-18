"""
API Reference - Database Manager
Dokumentasi lengkap semua method yang tersedia
"""

# ============================================================================
# GoogleSheetsManager Class
# ============================================================================

"""
Location: handlers/database.py

INITIALIZATION
──────────────
from handlers.database import get_db_manager

db = get_db_manager()
# Atau
from handlers.database import init_db_manager
db = init_db_manager()


METHOD: get_faq_data(refresh=False) -> list
──────────────────────────────────────────
Get all FAQ records from cache atau refresh dari Sheets.

Parameters:
  - refresh (bool): Jika True, fetch fresh dari Google Sheets
  
Returns:
  - List of FAQ dictionaries

Example:
  faq_list = db.get_faq_data()
  faq_list = db.get_faq_data(refresh=True)  # Force refresh
  
  for faq in faq_list:
      print(faq['button_label'])
      print(faq['response_text'])


METHOD: find_faq_by_trigger(trigger_id) -> dict | None
────────────────────────────────────────────────────
Find single FAQ by trigger ID.

Parameters:
  - trigger_id (str): Trigger ID dari FAQ

Returns:
  - FAQ dictionary atau None jika tidak ditemukan

Example:
  faq = db.find_faq_by_trigger("pricing_1")
  if faq:
      print(faq['response_text'])


METHOD: save_lead(discord_tag, name, order_id, issue_type, status="PENDING") -> bool
──────────────────────────────────────────────────────────────────────────────────
Save customer lead ke Google Sheets.

Parameters:
  - discord_tag (str): Discord tag user (misal: "User#1234")
  - name (str): Nama lengkap customer
  - order_id (str): Nomor order/invoice
  - issue_type (str): Tipe masalah (misal: "Barang Belum Sampai")
  - status (str): Initial status (default: "PENDING")

Returns:
  - True jika berhasil, False jika error

Example:
  success = db.save_lead(
      discord_tag="Budi#1234",
      name="Budi Santoso",
      order_id="#12345",
      issue_type="Barang Belum Sampai",
      status="PENDING"
  )
  
  if success:
      print("Lead saved successfully")


METHOD: update_lead_status(order_id, new_status) -> bool
────────────────────────────────────────────────────
Update status dari lead berdasarkan order_id.

Parameters:
  - order_id (str): Nomor order untuk diupdate
  - new_status (str): Status baru (PENDING, IN_PROGRESS, RESOLVED, dll)

Returns:
  - True jika berhasil, False jika error

Example:
  success = db.update_lead_status("#12345", "IN_PROGRESS")
  if success:
      print("Status updated")


METHOD: log_analytics(total_tickets, unresolved_queries) -> bool
────────────────────────────────────────────────────────────
Log analytics data.

Parameters:
  - total_tickets (int): Total tickets hari ini
  - unresolved_queries (int): Jumlah query yang belum selesai

Returns:
  - True jika berhasil, False jika error

Example:
  db.log_analytics(
      total_tickets=15,
      unresolved_queries=3
  )


METHOD: get_all_leads(limit=50) -> list
─────────────────────────────────────
Get all lead records dengan limit.

Parameters:
  - limit (int): Jumlah maksimal records (default: 50)

Returns:
  - List of lead dictionaries (yang paling baru dulu)

Example:
  recent_leads = db.get_all_leads(limit=100)
  for lead in recent_leads:
      print(f"Order: {lead['order_id']}, Status: {lead['status']}")


METHOD: reload_faq_cache() -> None
──────────────────────────────────
Reload FAQ cache dari Google Sheets.

Returns:
  - None

Example:
  db.reload_faq_cache()  # Called by !reload command


PROPERTIES
──────────

db.faq_cache
  - Cache dari FAQ data (list)
  - Auto-populated saat initialization
  - Updated dengan reload_faq_cache()

db.spreadsheet
  - gspread.Spreadsheet object
  - Raw access ke spreadsheet jika butuh advanced operations

db.client
  - gspread.Client object
  - Raw access ke Google Sheets API
"""

# ============================================================================
# Discord Commands Reference
# ============================================================================

"""
Location: handlers/commands.py

COMMAND: !support
─────────────────
Open main support menu.

Usage:
  !support

Result:
  - Menu embed dengan 3 buttons
  - Buttons: View FAQ, Contact Support, Check Status

Permissions:
  - None (all users)


COMMAND: !faq
──────────
List all FAQ.

Usage:
  !faq

Result:
  - Embed dengan semua FAQ
  - Setiap FAQ jadi button
  - Click button untuk lihat jawaban

Permissions:
  - None (all users)


COMMAND: !reload
───────────────
Reload FAQ data dari Google Sheets.

Usage:
  !reload

Result:
  - FAQ cache diupdate
  - Confirmation message

Permissions:
  - Administrator only


COMMAND: !stats
──────────────
Show support statistics.

Usage:
  !stats

Result:
  - Embed dengan:
    * Total tickets
    * Pending tickets
    * Resolved tickets
    * Bot info

Permissions:
  - Administrator only
"""

# ============================================================================
# Discord Events Reference
# ============================================================================

"""
Location: handlers/events.py

EVENT: on_ready()
─────────────────
Triggered when bot successfully connects to Discord.

What happens:
  - Bot status updated
  - Database initialized
  - Logging info

Usage:
  - Automatic (don't call manually)


EVENT: on_message(message)
──────────────────────────
Triggered when message sent.

What happens:
  - Ignore bot messages
  - Log thread messages
  - Process commands

Usage:
  - Automatic (don't call manually)


EVENT: on_command_error(ctx, error)
───────────────────────────────────
Triggered when command error.

What happens:
  - Send error embed to user
  - Log error
  - Provide helpful message

Usage:
  - Automatic (don't call manually)


EVENT: on_guild_join(guild)
───────────────────────────
Triggered when bot joins new server.

What happens:
  - Log join
  - Update bot presence

Usage:
  - Automatic (don't call manually)


EVENT: on_guild_remove(guild)
─────────────────────────────
Triggered when bot removed from server.

What happens:
  - Log removal
  - Alert admin

Usage:
  - Automatic (don't call manually)
"""

# ============================================================================
# Discord Views & Modals Reference
# ============================================================================

"""
Location: handlers/modals.py

CLASS: SupportModal(Modal)
──────────────────────────
Form modal untuk user submit support request.

Fields:
  - Name (required, max 100 chars)
  - Order ID (required, max 50 chars)
  - Issue Type (required, max 100 chars)
  - Description (required, max 1000 chars, paragraph)

When submitted:
  - Data saved to Google Sheets
  - Confirmation sent to user
  - Staff notified via notification channel

Usage:
  from handlers.modals import SupportModal
  await interaction.response.send_modal(SupportModal())


CLASS: TicketActionView(View)
─────────────────────────────
View with buttons untuk staff manage tickets.

Buttons:
  - "Take Ticket": Staff ambil ticket, create private thread
  - "Close Ticket": Close ticket, update status

Usage:
  - Auto-created saat staff notified
  - Biasanya tidak call manual


CLASS: SupportMenuView(View)
────────────────────────────
Main menu buttons untuk support.

Buttons:
  - "View FAQ": Show FAQ list
  - "Contact Support": Show modal
  - "Check Status": Status info

Usage:
  - Auto-created di !support command
  - Biasanya tidak call manual


CLASS: FAQView(View)
────────────────────
Dynamic FAQ buttons.

Buttons:
  - Dynamic: Button untuk setiap FAQ
  - Max 24 buttons (Discord limit)

Usage:
  - Auto-created di !faq command
  - Biasanya tidak call manual
"""

# ============================================================================
# Utility Functions Reference
# ============================================================================

"""
Location: utils/logger.py

FUNCTION: setup_logger(name: str) -> logging.Logger
────────────────────────────────────────────────────
Setup logger dengan file dan console output.

Parameters:
  - name (str): Logger name (misal: "MyModule")

Returns:
  - logging.Logger instance

Example:
  from utils.logger import setup_logger
  logger = setup_logger("MyModule")
  logger.info("Message")
  logger.error("Error")

Pre-configured loggers:
  - bot_logger: Main bot logging
  - db_logger: Database operations logging
  - event_logger: Discord events logging
"""

# ============================================================================
# Configuration Reference
# ============================================================================

"""
Location: config.py

VARIABLES
──────────

DISCORD_TOKEN (str)
  - Bot token dari Discord Developer Portal
  
DISCORD_GUILD_ID (int)
  - Guild ID untuk development (optional)

GOOGLE_SHEETS_ID (str)
  - Spreadsheet ID dari Google Sheets URL

CREDENTIALS_FILE (str)
  - Path ke credentials.json file

SUPPORT_CHANNEL_ID (int)
  - Channel ID untuk support requests

STAFF_NOTIFICATION_CHANNEL_ID (int)
  - Channel ID untuk staff notifications

LOGS_CHANNEL_ID (int)
  - Channel ID untuk bot logs

FAQ_TAB_NAME (str)
  - Tab name di Google Sheets untuk FAQ (default: "FAQ")

LEADS_TAB_NAME (str)
  - Tab name di Google Sheets untuk Leads (default: "Leads")

ANALYTICS_TAB_NAME (str)
  - Tab name di Google Sheets untuk Analytics (default: "Analytics")

LOG_LEVEL (str)
  - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL

DEBUG_MODE (bool)
  - Enable debug mode (True/False)

BASE_DIR (str)
  - Project root directory path

LOGS_DIR (str)
  - Directory untuk log files

DATA_DIR (str)
  - Directory untuk data files
"""

# ============================================================================
# Error Handling
# ============================================================================

"""
Exceptions yang mungkin:

FileNotFoundError
  - credentials.json tidak ditemukan
  - Fix: Download dari Google Cloud Console

gspread.exceptions.SpreadsheetNotFound
  - Google Sheets ID tidak valid
  - Fix: Copy correct Sheet ID dari URL

gspread.exceptions.WorksheetNotFound
  - Tab name tidak ditemukan
  - Fix: Create tabs atau fix TAB_NAME di config

discord.errors.LoginFailure
  - Bot token invalid
  - Fix: Copy token baru dari Developer Portal

discord.errors.HTTPException
  - API call error
  - Fix: Check logs dan retry

ConnectionError
  - Network error
  - Fix: Check internet connection
"""
