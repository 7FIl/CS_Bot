"""
Discord Bot CLI Control Panel
Interactive CLI interface for managing the Discord Customer Support Bot

Author: 7Fil
Version: 1.0.1
"""

import os
import sys
import asyncio
import json
import threading
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows
init(autoreset=True)

# Import bot components
from config import DISCORD_TOKEN, PREFIX, DEBUG_MODE, GOOGLE_SHEETS_ID
from utils.logger import bot_logger
from handlers.database import get_db_manager, init_db_manager

# Global variables
bot_instance = None
bot_task = None
bot_running = False
bot_thread = None


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header."""
    pass


def print_status(db_manager=None):
    """Print current bot status."""
    global bot_running, bot_instance
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}STATUS")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Bot status - use bot_running flag for consistency with menu
    if bot_running:
        print(f"{Fore.GREEN}● Bot Status: ONLINE{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}● Bot Status: OFFLINE{Style.RESET_ALL}")
    
    # Database status
    try:
        if db_manager:
            print(f"{Fore.GREEN}● Database: CONNECTED{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}● Database: NOT CONNECTED{Style.RESET_ALL}")
    except:
        print(f"{Fore.RED}● Database: ERROR{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def print_menu():
    """Print the main menu."""
    global bot_running
    
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}MAIN MENU{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
    
    # Show Start or Stop based on bot status
    if bot_running:
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Stop Bot")
    else:
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Start Bot")
    
    print(f"{Fore.GREEN}2.{Style.RESET_ALL} Manage Admin Roles")
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} Manage FAQs")
    print(f"{Fore.GREEN}4.{Style.RESET_ALL} Settings")
    print(f"{Fore.GREEN}5.{Style.RESET_ALL} Refresh Database")
    print(f"{Fore.GREEN}6.{Style.RESET_ALL} View Logs")
    print(f"{Fore.GREEN}7.{Style.RESET_ALL} View Bot Statistics")
    print(f"{Fore.RED}0.{Style.RESET_ALL} Exit")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")


def load_admin_roles():
    """Load admin roles from config file."""
    config_file = "admin_roles.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return data.get('admin_roles', [])
        except Exception as e:
            print(f"{Fore.RED}Error loading admin roles: {e}{Style.RESET_ALL}")
            return []
    return []


def load_settings():
    """Load bot settings from config file."""
    config_file = "bot_settings.json"
    default_settings = {
        'notify_admins_on_ticket': True
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"{Fore.RED}Error loading settings: {e}{Style.RESET_ALL}")
            return default_settings
    return default_settings


def save_settings(settings):
    """Save bot settings to config file."""
    config_file = "bot_settings.json"
    try:
        with open(config_file, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving settings: {e}{Style.RESET_ALL}")
        return False


def save_admin_roles(roles):
    """Save admin roles to config file."""
    config_file = "admin_roles.json"
    try:
        with open(config_file, 'w') as f:
            json.dump({'admin_roles': roles}, f, indent=4)
        print(f"{Fore.GREEN}✓ Admin roles saved successfully{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Error saving admin roles: {e}{Style.RESET_ALL}")
        return False


def run_bot_thread():
    """Run bot in separate thread."""
    global bot_instance, bot_running
    
    try:
        # Disable console logging to keep CLI clean
        from utils.logger import disable_console_logging
        disable_console_logging()
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Import and setup bot - reimport to get fresh instance
        import importlib
        import sys
        
        # Clear the main module from cache to get a fresh bot instance
        if 'main' in sys.modules:
            importlib.reload(sys.modules['main'])
        
        from main import bot, load_cogs
        from handlers.database import init_db_manager
        
        bot_instance = bot
        
        # Initialize database
        try:
            db_manager = init_db_manager()
            print(f"{Fore.GREEN}✓ Database connected successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Database connection failed: {e}{Style.RESET_ALL}")
            bot_running = False
            return
        
        # Load cogs
        loop.run_until_complete(load_cogs())
        print(f"{Fore.GREEN}✓ Cogs loaded successfully{Style.RESET_ALL}")
        
        # Start bot
        print(f"{Fore.GREEN}✓ Connecting to Discord...{Style.RESET_ALL}")
        loop.run_until_complete(bot.start(DISCORD_TOKEN))
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "Event loop is closed" not in str(e):
            print(f"{Fore.RED}✗ Bot error: {e}{Style.RESET_ALL}")
        bot_running = False
    finally:
        # Cleanup
        try:
            if bot_instance and not bot_instance.is_closed():
                loop.run_until_complete(bot_instance.close())
        except:
            pass
        try:
            loop.close()
        except:
            pass


def start_bot():
    """Start the Discord bot."""
    global bot_running, bot_thread
    
    if bot_running:
        print(f"\n{Fore.YELLOW}⚠ Bot is already running!{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    clear_screen()
    print_header()
    print(f"\n{Fore.CYAN}Starting Discord bot...{Style.RESET_ALL}")
    
    bot_running = True
    bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    
    # Wait for bot to initialize and show status
    import time
    time.sleep(4)
    
    print(f"\n{Fore.GREEN}✓ Bot started successfully!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}(View logs menu for detailed activity){Style.RESET_ALL}")
    input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")


def stop_bot(skip_confirm=False):
    """Stop the Discord bot."""
    global bot_running, bot_instance
    
    if not bot_running:
        if not skip_confirm:
            print(f"{Fore.YELLOW}⚠ Bot is not running!{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    if not skip_confirm:
        confirm = input(f"\n{Fore.YELLOW}Are you sure you want to stop the bot? (y/n): {Style.RESET_ALL}")
        if confirm.lower() != 'y':
            return
    
    print(f"\n{Fore.CYAN}Stopping Discord bot...{Style.RESET_ALL}")
    
    try:
        if bot_instance and bot_instance.loop and not bot_instance.is_closed():
            # Properly close the bot
            future = asyncio.run_coroutine_threadsafe(bot_instance.close(), bot_instance.loop)
            future.result(timeout=5)  # Wait up to 5 seconds for clean shutdown
        
        bot_running = False
        import time
        time.sleep(1)  # Give connections time to close
        print(f"{Fore.GREEN}✓ Bot stopped successfully{Style.RESET_ALL}")
    except Exception as e:
        bot_running = False
        # Suppress error display to user
        pass
    
    if not skip_confirm:
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def manage_admin_roles():
    """Manage admin roles menu."""
    while True:
        clear_screen()
        print_header()
        
        roles = load_admin_roles()
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}ADMIN ROLES MANAGEMENT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        if roles:
            print(f"\n{Fore.GREEN}Current Admin Roles:{Style.RESET_ALL}")
            for i, role in enumerate(roles, 1):
                print(f"  {i}. {role}")
        else:
            print(f"\n{Fore.YELLOW}No admin roles configured{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Add Role")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} Remove Role")
        print(f"{Fore.RED}0.{Style.RESET_ALL} Back to Main Menu")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '1':
            role_name = input(f"\n{Fore.CYAN}Enter role name (case-sensitive): {Style.RESET_ALL}")
            if role_name:
                if role_name not in roles:
                    roles.append(role_name)
                    # Save immediately after adding
                    if save_admin_roles(roles):
                        print(f"{Fore.GREEN}✓ Role added and saved: {role_name}{Style.RESET_ALL}")
                    else:
                        roles.remove(role_name)  # Rollback if save fails
                else:
                    print(f"{Fore.YELLOW}⚠ Role already exists!{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        elif choice == '2':
            if roles:
                try:
                    idx = int(input(f"\n{Fore.CYAN}Enter role number to remove: {Style.RESET_ALL}")) - 1
                    if 0 <= idx < len(roles):
                        role_to_remove = roles[idx]
                        confirm = input(f"\n{Fore.YELLOW}Remove '{role_to_remove}'? (y/n): {Style.RESET_ALL}")
                        if confirm.lower() == 'y':
                            roles.pop(idx)
                            # Save immediately after removing
                            if save_admin_roles(roles):
                                print(f"{Fore.GREEN}✓ Role removed and saved: {role_to_remove}{Style.RESET_ALL}")
                            else:
                                roles.insert(idx, role_to_remove)  # Rollback if save fails
                        else:
                            print(f"{Fore.YELLOW}⚠ Removal cancelled{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ Invalid role number{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}✗ Invalid input{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ No roles to remove{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        elif choice == '0':
            break


def manage_settings():
    """Manage bot settings menu."""
    while True:
        clear_screen()
        print_header()
        
        settings = load_settings()
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}BOT SETTINGS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        # Display current settings
        print(f"\n{Fore.GREEN}Current Settings:{Style.RESET_ALL}\n")
        
        notify_status = f"{Fore.GREEN}ON{Style.RESET_ALL}" if settings.get('notify_admins_on_ticket', True) else f"{Fore.RED}OFF{Style.RESET_ALL}"
        print(f"  Notify Admins on Ticket: {notify_status}")
        print(f"    {Fore.CYAN}When enabled, admins will be tagged when users create support tickets{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Toggle Admin Notifications")
        print(f"{Fore.RED}0.{Style.RESET_ALL} Back to Main Menu")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '1':
            # Toggle the setting
            current_value = settings.get('notify_admins_on_ticket', True)
            settings['notify_admins_on_ticket'] = not current_value
            
            if save_settings(settings):
                new_status = "enabled" if settings['notify_admins_on_ticket'] else "disabled"
                print(f"\n{Fore.GREEN}✓ Admin notifications {new_status}!{Style.RESET_ALL}")
            else:
                # Rollback if save fails
                settings['notify_admins_on_ticket'] = current_value
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        
        elif choice == '0':
            break
        else:
            print(f"\n{Fore.RED}✗ Invalid choice. Please try again.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def manage_faqs():
    """Manage FAQs menu."""
    while True:
        clear_screen()
        print_header()
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}FAQ MANAGEMENT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} View All FAQs")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} Add New FAQ")
        print(f"{Fore.GREEN}3.{Style.RESET_ALL} Delete FAQ")
        print(f"{Fore.GREEN}4.{Style.RESET_ALL} Refresh FAQ List")
        print(f"{Fore.RED}0.{Style.RESET_ALL} Back to Main Menu")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '1':
            view_faqs()
        elif choice == '2':
            add_faq()
        elif choice == '3':
            delete_faq()
        elif choice == '4':
            refresh_faq_list()
        elif choice == '0':
            break


def view_faqs():
    """View all FAQs."""
    try:
        db = get_db_manager()
        faqs = db.get_faq_data(refresh=True)
        
        clear_screen()
        print_header()
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}CURRENT FAQs{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        if faqs:
            print(f"\n{Fore.GREEN}Total FAQs: {len(faqs)}{Style.RESET_ALL}\n")
            for i, faq in enumerate(faqs, 1):
                trigger = faq.get('trigger_id', 'N/A')
                label = faq.get('button_label', 'N/A')
                response = faq.get('response_text', 'N/A')
                
                print(f"{Fore.CYAN}[{i}] {Style.BRIGHT}Trigger:{Style.RESET_ALL} {trigger}")
                print(f"    {Style.BRIGHT}Label:{Style.RESET_ALL} {label}")
                print(f"    {Style.BRIGHT}Response:{Style.RESET_ALL} {response[:80]}{'...' if len(response) > 80 else ''}")
                print()
        else:
            print(f"\n{Fore.YELLOW}No FAQs found in database{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error loading FAQs: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def add_faq():
    """Add new FAQ."""
    clear_screen()
    print_header()
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}ADD NEW FAQ{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
    
    trigger_id = input(f"\n{Fore.CYAN}Trigger ID: {Style.RESET_ALL}")
    if not trigger_id:
        print(f"{Fore.RED}✗ Trigger ID cannot be empty{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    button_label = input(f"{Fore.CYAN}Button Label: {Style.RESET_ALL}")
    if not button_label:
        print(f"{Fore.RED}✗ Button Label cannot be empty{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Response Text (press ESC to finish):{Style.RESET_ALL}")
    
    # Use msvcrt for Windows to detect ESC key
    import msvcrt
    lines = []
    current_line = ""
    
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            
            # ESC key (0x1b)
            if char == b'\x1b':
                if current_line:
                    lines.append(current_line)
                break
            # Enter key (0x0d)
            elif char == b'\r':
                lines.append(current_line)
                current_line = ""
                print()  # New line
            # Backspace (0x08)
            elif char == b'\x08':
                if current_line:
                    current_line = current_line[:-1]
                    print('\b \b', end='', flush=True)
            # Regular character
            elif char >= b' ':
                current_line += char.decode('utf-8', errors='ignore')
                print(char.decode('utf-8', errors='ignore'), end='', flush=True)
    
    response_text = "\n".join(lines)
    print()  # New line after ESC
    
    if not response_text:
        print(f"{Fore.RED}✗ Response Text cannot be empty{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        db = get_db_manager()
        from config import FAQ_TAB_NAME
        faq_sheet = db.spreadsheet.worksheet(FAQ_TAB_NAME)
        
        # Append row
        faq_sheet.append_row([trigger_id, button_label, response_text])
        
        # Refresh cache
        db.reload_faq_cache()
        
        print(f"\n{Fore.GREEN}✓ FAQ added successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error adding FAQ: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def delete_faq():
    """Delete FAQ."""
    try:
        db = get_db_manager()
        faqs = db.get_faq_data(refresh=True)
        
        if not faqs:
            print(f"\n{Fore.YELLOW}⚠ No FAQs available to delete{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        clear_screen()
        print_header()
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}DELETE FAQ{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}\n")
        
        for i, faq in enumerate(faqs, 1):
            trigger = faq.get('trigger_id', 'N/A')
            label = faq.get('button_label', 'N/A')
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {trigger} - {label}")
        
        try:
            idx = int(input(f"\n{Fore.YELLOW}Enter FAQ number to delete (0 to cancel): {Style.RESET_ALL}")) - 1
            
            if idx == -1:
                return
            
            if 0 <= idx < len(faqs):
                faq_to_delete = faqs[idx]
                trigger_id = faq_to_delete.get('trigger_id', '')
                
                confirm = input(f"\n{Fore.RED}Delete FAQ '{trigger_id}'? This cannot be undone! (y/n): {Style.RESET_ALL}")
                if confirm.lower() == 'y':
                    from config import FAQ_TAB_NAME
                    faq_sheet = db.spreadsheet.worksheet(FAQ_TAB_NAME)
                    
                    # Delete row (index + 2 because: +1 for header, +1 for 0-based to 1-based)
                    faq_sheet.delete_rows(idx + 2)
                    
                    # Refresh cache
                    db.reload_faq_cache()
                    
                    print(f"\n{Fore.GREEN}✓ FAQ deleted successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Invalid FAQ number{Style.RESET_ALL}")
        except ValueError:
            print(f"\n{Fore.RED}✗ Invalid input{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error deleting FAQ: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def refresh_faq_list():
    """Refresh FAQ list from database."""
    try:
        db = get_db_manager()
        db.reload_faq_cache()
        print(f"\n{Fore.GREEN}✓ FAQ list refreshed successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error refreshing FAQ list: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def refresh_database():
    """Refresh database cache."""
    try:
        if not bot_running:
            print(f"\n{Fore.YELLOW}⚠ Please start the bot first!{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        db = get_db_manager()
        db.reload_faq_cache()
        
        print(f"\n{Fore.GREEN}✓ Database cache refreshed successfully!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Bot now has the latest data{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error refreshing database: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_logs():
    """View recent logs."""
    clear_screen()
    print_header()
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}RECENT LOGS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}\n")
    
    # Get today's log file with correct format
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = f"logs/bot_{date_str}.log"
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 50 lines
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                if recent_lines:
                    for line in recent_lines:
                        # Color code based on log level
                        if 'ERROR' in line:
                            print(f"{Fore.RED}{line.strip()}{Style.RESET_ALL}")
                        elif 'WARNING' in line:
                            print(f"{Fore.YELLOW}{line.strip()}{Style.RESET_ALL}")
                        elif 'INFO' in line:
                            print(f"{Fore.GREEN}{line.strip()}{Style.RESET_ALL}")
                        else:
                            print(line.strip())
                else:
                    print(f"{Fore.YELLOW}Log file is empty{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Error reading logs: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No log file found for today{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Expected: {log_file}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_statistics():
    """View bot statistics."""
    clear_screen()
    print_header()
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}BOT STATISTICS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}\n")
    
    if not bot_running or not bot_instance or not bot_instance.is_ready():
        print(f"{Fore.RED}✗ Bot is not running or not ready{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        print(f"{Fore.GREEN}{Style.BRIGHT}Bot Information:{Style.RESET_ALL}")
        print(f"  Bot Name: {bot_instance.user.name}")
        print(f"  Bot ID: {bot_instance.user.id}")
        print(f"  Servers: {len(bot_instance.guilds)}")
        print(f"  Prefix: {PREFIX}")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Database Information:{Style.RESET_ALL}")
        print(f"  Sheets ID: {GOOGLE_SHEETS_ID[:30]}...")
        
        db = get_db_manager()
        faqs = db.get_faq_data()
        print(f"  Total FAQs: {len(faqs)}")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Admin Roles:{Style.RESET_ALL}")
        roles = load_admin_roles()
        if roles:
            for role in roles:
                print(f"  • {role}")
        else:
            print(f"  {Fore.YELLOW}No admin roles configured{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error getting statistics: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def main():
    """Main function."""
    # Initialize database
    try:
        db_manager = init_db_manager()
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to connect to database: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please check your credentials.json file{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    while True:
        clear_screen()
        print_header()
        print_status(db_manager)
        print_menu()
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")
        
        if choice == '1':
            # Dynamic option: Start or Stop based on bot status
            if bot_running:
                stop_bot()
            else:
                start_bot()
        elif choice == '2':
            manage_admin_roles()
        elif choice == '3':
            manage_faqs()
        elif choice == '4':
            manage_settings()
        elif choice == '5':
            refresh_database()
        elif choice == '6':
            view_logs()
        elif choice == '7':
            view_statistics()
        elif choice == '0':
            if bot_running:
                confirm = input(f"\n{Fore.RED}Bot is still running. Stop and exit? (y/n): {Style.RESET_ALL}")
                if confirm.lower() == 'y':
                    stop_bot(skip_confirm=True)
                    break
            else:
                break
        else:
            print(f"\n{Fore.RED}✗ Invalid choice. Please try again.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Thank you for using Discord Bot CLI!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}\n")


if __name__ == "__main__":
    import warnings
    import sys
    
    # Suppress all aiohttp and asyncio warnings
    warnings.filterwarnings('ignore', category=ResourceWarning)
    warnings.filterwarnings('ignore', message='Unclosed connector')
    warnings.filterwarnings('ignore', message='Unclosed client session')
    warnings.filterwarnings('ignore', message='Task was destroyed but it is pending')
    warnings.filterwarnings('ignore', module='aiohttp')
    
    # Redirect stderr temporarily to suppress final cleanup messages
    import io
    original_stderr = sys.stderr
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}✓ Exiting...{Style.RESET_ALL}")
    finally:
        # Clean shutdown
        if bot_running and bot_instance:
            try:
                # Suppress output during final cleanup
                sys.stderr = io.StringIO()
                if bot_instance.loop and not bot_instance.is_closed():
                    future = asyncio.run_coroutine_threadsafe(bot_instance.close(), bot_instance.loop)
                    try:
                        future.result(timeout=3)
                    except:
                        pass
            except:
                pass
            finally:
                sys.stderr = original_stderr
        sys.exit(0)
