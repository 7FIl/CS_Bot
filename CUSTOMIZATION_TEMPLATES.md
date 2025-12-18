"""
TEMPLATE FILE - Untuk Ekspansi & Customization

File ini berisi template dan contoh code untuk expand functionality bot.
Copy paste dan customize sesuai kebutuhan Anda.
"""

# ============================================================================
# TEMPLATE 1: MENAMBAH CUSTOM COMMAND
# ============================================================================

"""
Tempat: handlers/commands.py
Caranya: 

class SupportCommands(commands.Cog):
    def __init__(self, bot_instance):
        self.bot = bot_instance
        global bot
        bot = bot_instance
    
    # TAMBAHKAN COMMAND INI:
    
    @commands.command(
        name='mycustom',
        description='Deskripsi command',
        help='Help text'
    )
    @commands.has_role("Staff")  # Optional: require role
    async def my_custom_command(self, ctx: commands.Context, *, message: str) -> None:
        \"\"\"Custom command template.\"\"\"
        try:
            # Your logic here
            embed = discord.Embed(
                title="My Custom Command",
                description=f"You said: {message}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            event_logger.error(f"Error di my_custom_command: {str(e)}")
            await ctx.send("Error occurred", delete_after=10)


# Usage: !mycustom hello
"""

# ============================================================================
# TEMPLATE 2: MENAMBAH NEW BUTTON DENGAN ACTION
# ============================================================================

"""
Tempat: handlers/modals.py atau handlers/commands.py
Caranya:

class CustomView(View):
    def __init__(self, order_id: str):
        super().__init__(timeout=600)
        self.order_id = order_id
    
    @discord.ui.button(
        label="Custom Action",
        style=discord.ButtonStyle.primary,
        custom_id="custom_action"
    )
    async def custom_button(self, interaction: discord.Interaction, button: Button) -> None:
        \"\"\"Handle custom button click.\"\"\"
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Your action here
            result = await self.process_action()
            
            if result:
                embed = discord.Embed(
                    title="✅ Action Success",
                    description="Action berhasil diproses",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Action Failed",
                    description="Terjadi error",
                    color=discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            event_logger.error(f"Error di custom_button: {str(e)}")
    
    async def process_action(self) -> bool:
        \"\"\"Process your custom action.\"\"\"
        # Your logic
        return True
"""

# ============================================================================
# TEMPLATE 3: MENAMBAH DATABASE METHOD
# ============================================================================

"""
Tempat: handlers/database.py
Caranya: Di class GoogleSheetsManager, tambahkan method baru:

def save_custom_data(self, data_dict: dict) -> bool:
    \"\"\"
    Save custom data ke Google Sheets.
    
    Args:
        data_dict: Dictionary dengan data
        
    Returns:
        True jika berhasil, False jika error
    \"\"\"
    try:
        # Create atau open your custom sheet
        sheet = self.spreadsheet.worksheet("CustomTab")
        
        # Convert dict ke list untuk append_row
        row_data = list(data_dict.values())
        
        # Append ke sheet
        sheet.append_row(row_data)
        db_logger.info(f"Custom data saved: {data_dict}")
        return True
        
    except Exception as e:
        db_logger.error(f"Error saat save custom data: {str(e)}")
        return False


def get_custom_data(self, filter_key: str = None) -> list:
    \"\"\"
    Get custom data dari Google Sheets.
    
    Args:
        filter_key: Optional filter key
        
    Returns:
        List of records
    \"\"\"
    try:
        sheet = self.spreadsheet.worksheet("CustomTab")
        records = sheet.get_all_records()
        
        if filter_key:
            # Apply filter if needed
            records = [r for r in records if filter_key in str(r)]
        
        return records
        
    except Exception as e:
        db_logger.error(f"Error saat get custom data: {str(e)}")
        return []
"""

# ============================================================================
# TEMPLATE 4: MENAMBAH SCHEDULED TASK
# ============================================================================

"""
Tempat: main.py (import tasks)
Caranya: Add di top level

from discord.ext import commands, tasks

Kemudian di bot setup:

@tasks.loop(hours=1)  # Run every hour
async def check_pending_tickets():
    \"\"\"Check pending tickets dan auto-escalate jika needed.\"\"\"
    try:
        db = get_db_manager()
        leads = db.get_all_leads()
        
        for lead in leads:
            if lead['status'] == 'PENDING':
                # Check if pending > 24 hours
                # If yes, escalate
                pass
        
    except Exception as e:
        event_logger.error(f"Error di check_pending_tickets: {str(e)}")

@check_pending_tickets.before_loop
async def before_check_pending_tickets():
    \"\"\"Wait until bot ready before first run.\"\"\"
    await bot.wait_until_ready()

# Then start the task in on_ready()
@commands.Cog.listener()
async def on_ready(self):
    if not check_pending_tickets.is_running():
        check_pending_tickets.start()
"""

# ============================================================================
# TEMPLATE 5: MENAMBAH MODAL FIELD
# ============================================================================

"""
Tempat: handlers/modals.py
Caranya: Di class SupportModal, tambahkan field:

class SupportModal(Modal):
    def __init__(self):
        super().__init__(title="Hubungi Support", timeout=600)
        
        # TAMBAHKAN INI:
        self.phone_input = TextInput(
            label="Nomor Telepon",
            placeholder="Masukkan nomor telepon",
            required=True,
            max_length=20
        )
        self.add_item(self.phone_input)
        
        # Tambahkan field baru lainnya sesuai kebutuhan
    
    async def on_submit(self, interaction):
        # Field baru bisa diakses dengan: self.phone_input.value
        phone = self.phone_input.value
        # ... rest of code
"""

# ============================================================================
# TEMPLATE 6: MENAMBAH ERROR HANDLER
# ============================================================================

"""
Tempat: handlers/events.py
Caranya: Di class Events, tambahkan:

@commands.Cog.listener()
async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    \"\"\"Handle slash command errors.\"\"\"
    try:
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Anda tidak punya permission untuk command ini",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        else:
            event_logger.error(f"App command error: {str(error)}")
            embed = discord.Embed(
                title="❌ Error",
                description="Terjadi error saat memproses command",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    except Exception as e:
        event_logger.error(f"Error di error handler: {str(e)}")
"""

# ============================================================================
# TEMPLATE 7: MENAMBAH LOGGING/TRACKING
# ============================================================================

"""
Tempat: handlers/modals.py atau handlers/commands.py
Caranya:

from utils.logger import setup_logger

# Create custom logger for your feature
custom_logger = setup_logger("MyFeature")

# Use it:
custom_logger.info("Action happened")
custom_logger.warning("Something unusual")
custom_logger.error("Error occurred")

# Logs akan di-save di: logs/bot_YYYY-MM-DD.log
"""

# ============================================================================
# TEMPLATE 8: MENAMBAH PERMISSION CHECK
# ============================================================================

"""
Tempat: handlers/commands.py
Caranya:

# Option 1: Require specific role
@commands.command()
@commands.has_role("Admin")
async def admin_command(ctx):
    await ctx.send("Only admin can use this")

# Option 2: Require permission
@commands.command()
@commands.has_permissions(administrator=True)
async def admin_only(ctx):
    await ctx.send("Admin only")

# Option 3: Custom check
def is_staff():
    async def predicate(ctx):
        # Your logic
        return user_is_staff
    return commands.check(predicate)

@commands.command()
@is_staff()
async def staff_command(ctx):
    await ctx.send("Staff only")
"""

# ============================================================================
# TEMPLATE 9: MENAMBAH EMBED TEMPLATE
# ============================================================================

"""
Tempat: Anywhere dalam code
Caranya:

# Create reusable embed template
def create_success_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f"✅ {title}",
        description=message,
        color=discord.Color.green()
    )

def create_error_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f"❌ {title}",
        description=message,
        color=discord.Color.red()
    )

def create_info_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f"ℹ️ {title}",
        description=message,
        color=discord.Color.blue()
    )

# Usage:
embed = create_success_embed("Action Complete", "Your message here")
await ctx.send(embed=embed)
"""

# ============================================================================
# TEMPLATE 10: MENAMBAH WEBHOOK
# ============================================================================

"""
Tempat: handlers/commands.py atau handlers/events.py
Caranya:

import aiohttp

async def send_webhook(webhook_url: str, data: dict) -> bool:
    \"\"\"Send data to external webhook.\"\"\"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=data) as resp:
                if resp.status == 200:
                    event_logger.info("Webhook sent successfully")
                    return True
                else:
                    event_logger.error(f"Webhook failed: {resp.status}")
                    return False
    except Exception as e:
        event_logger.error(f"Error sending webhook: {str(e)}")
        return False

# Usage:
data = {
    "event": "ticket_created",
    "order_id": "#12345",
    "status": "PENDING"
}
await send_webhook("https://yourapi.com/webhook", data)
"""

# ============================================================================
# TIPS UNTUK CUSTOMIZE
# ============================================================================

"""
Best Practices Saat Customize:

1. SEMPRE TEST LOCALLY
   - Run bot locally dulu
   - Test di Discord
   - Check logs

2. JANGAN UBAH CORE LOGIC
   - Jangan edit main database flow
   - Jangan remove error handling
   - Jangan hardcode values

3. USE CONFIGURATION
   - Add new config ke config.py jika needed
   - Use environment variables
   - Don't hardcode secrets

4. FOLLOW CODE STYLE
   - Follow existing patterns
   - Use consistent naming
   - Add docstrings

5. LOG EVERYTHING
   - Log important actions
   - Log errors
   - Log for debugging

6. BACKUP BEFORE CHANGE
   - Backup file sebelum edit
   - Use git untuk version control
   - Test thoroughly

7. DOCUMENT CHANGES
   - Add comments explaining changes
   - Update docstrings
   - Keep changelog
"""

# ============================================================================
# COMMON CUSTOMIZATION SCENARIOS
# ============================================================================

"""
Scenario 1: Tambah Priority System
─────────────────────────────────────
1. Add "priority" field ke modal
2. Add "priority" column ke Google Sheets Leads tab
3. Update save_lead() method untuk include priority
4. Update sorting/display untuk filter by priority

Scenario 2: Tambah Urgency Alerts
──────────────────────────────────
1. Add scheduled task di main.py
2. Check for pending tickets > X hours
3. Send alert to staff channel
4. Auto-escalate if needed

Scenario 3: Tambah Customer Feedback Form
───────────────────────────────────────────
1. Create new modal: FeedbackModal
2. Add command: !feedback
3. Add new Google Sheets tab: Feedback
4. Log data dengan timestamp

Scenario 4: Tambah Auto-Response
──────────────────────────────────
1. Create response templates di Google Sheets
2. Auto-send ke user DM
3. Custom message based on issue_type
4. Include reference number

Scenario 5: Tambah Analytics Dashboard
───────────────────────────────────────
1. Create command: !analytics
2. Query Google Sheets untuk data
3. Calculate metrics
4. Create chart/summary embed
"""
