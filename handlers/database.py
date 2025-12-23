import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from config import GOOGLE_SHEETS_ID, CREDENTIALS_FILE, FAQ_TAB_NAME, LEADS_TAB_NAME, ANALYTICS_TAB_NAME
from utils.logger import db_logger

class GoogleSheetsManager:
    """Manager for Google Sheets integration."""
    
    def __init__(self):
        """Initialize Google Sheets connection."""
        try:
            self.scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate using service account
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_FILE, 
                self.scope
            )
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            db_logger.info("Successfully connected to Google Sheets")
            
            # Cache FAQ data on startup
            self.faq_cache = None
            self.reload_faq_cache()
            
        except FileNotFoundError:
            db_logger.error(f"Credentials file '{CREDENTIALS_FILE}' not found!")
            raise
        except Exception as e:
            db_logger.error(f"Error initializing Google Sheets: {str(e)}")
            raise
    
    def reload_faq_cache(self):
        """Reload FAQ cache from Sheets."""
        try:
            faq_sheet = self.spreadsheet.worksheet(FAQ_TAB_NAME)
            # Specify expected headers to avoid duplicate header error
            self.faq_cache = faq_sheet.get_all_records(expected_headers=['trigger_id', 'button_label', 'response_text'])
            db_logger.info(f"FAQ cache reloaded. Total FAQ: {len(self.faq_cache)}")
        except Exception as e:
            db_logger.error(f"Error reloading FAQ cache: {str(e)}")
            self.faq_cache = []
    
    def get_faq_data(self, refresh: bool = False) -> list:
        """
        Get FAQ data from cache or Sheets.
        
        Args:
            refresh: If True, refresh from Sheets
            
        Returns:
            List of FAQ records
        """
        if refresh or self.faq_cache is None:
            self.reload_faq_cache()
        return self.faq_cache if self.faq_cache else []
    
    def find_faq_by_trigger(self, trigger_id: str) -> dict:
        """
        Find FAQ by trigger_id.
        
        Args:
            trigger_id: FAQ trigger button ID
            
        Returns:
            FAQ record or None if not found
        """
        faq_data = self.get_faq_data()
        for faq in faq_data:
            if str(faq.get('trigger_id', '')).strip().lower() == str(trigger_id).strip().lower():
                return faq
        return None
    
    def get_next_ticket_number(self) -> int:
        """
        Get next ticket number.
        
        Returns:
            Ticket number
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            all_records = leads_sheet.get_all_records()
            
            # If no records yet, start from 1
            if not all_records:
                return 1
            
            # Find highest number - use 'ticket_number' matching sheet header
            max_number = 0
            for record in all_records:
                try:
                    ticket_num = int(record.get('ticket_number', 0) or 0)
                    max_number = max(max_number, ticket_num)
                except:
                    pass
            
            return max_number + 1
            
        except Exception as e:
            db_logger.error(f"Error getting next ticket number: {str(e)}")
            return 1
    
    def save_lead(self, discord_tag: str, name: str, order_id: str, 
                  issue_type: str, status: str = "PENDING") -> tuple:
        """
        Save lead data to Leads tab.
        
        Args:
            discord_tag: User's Discord tag
            name: User's name
            order_id: User's order ID
            issue_type: Issue type
            status: Ticket status
            
        Returns:
            Tuple (success: bool, ticket_number: int)
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Get next ticket number
            ticket_number = self.get_next_ticket_number()
            
            # Format timestamp
            tz = pytz.timezone('Asia/Jakarta')
            timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare data in order: timestamp, ticket_number, discord_tag, name, order_id, issue_type, status
            row_data = [timestamp, ticket_number, discord_tag, name, order_id, issue_type, status]
            
            # Append to sheet
            leads_sheet.append_row(row_data)
            db_logger.info(f"New lead saved: #{ticket_number} {name} ({order_id})")
            return (True, ticket_number)
            
        except Exception as e:
            db_logger.error(f"Error saving lead: {str(e)}")
            return (False, 0)
    
    def update_lead_status(self, order_id: str, new_status: str) -> bool:
        """
        Update lead status by order_id.
        
        Args:
            order_id: Order ID to update
            new_status: New status (PENDING, IN_PROGRESS, RESOLVED, CLOSED)
            
        Returns:
            True if successful, False if failed
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Find row with order_id
            all_records = leads_sheet.get_all_records()
            for idx, record in enumerate(all_records, start=2):  # start=2 because header is in row 1
                if str(record.get('order_id', '')).strip() == str(order_id).strip():
                    # Column 7 = status (timestamp, ticket_number, discord_tag, name, order_id, issue_type, status)
                    leads_sheet.update_cell(idx, 7, new_status)
                    db_logger.info(f"Lead status {order_id} updated to {new_status}")
                    return True
            
            db_logger.warning(f"Order ID {order_id} not found")
            return False
            
        except Exception as e:
            db_logger.error(f"Error updating lead status: {str(e)}")
            return False
    
    def log_analytics(self, total_tickets: int, unresolved_queries: int) -> bool:
        """
        Log analytics data.
        
        Args:
            total_tickets: Total tickets today
            unresolved_queries: Total unresolved queries
            
        Returns:
            True if successful, False if failed
        """
        try:
            analytics_sheet = self.spreadsheet.worksheet(ANALYTICS_TAB_NAME)
            
            date_str = datetime.now().strftime('%Y-%m-%d')
            row_data = [date_str, total_tickets, unresolved_queries]
            
            analytics_sheet.append_row(row_data)
            db_logger.info(f"Analytics data logged: {total_tickets} tickets, {unresolved_queries} unresolved")
            return True
            
        except Exception as e:
            db_logger.error(f"Error logging analytics: {str(e)}")
            return False
    
    def get_all_leads(self, limit: int = 50) -> list:
        """
        Get all leads data (for reporting).
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of lead records
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            all_records = leads_sheet.get_all_records()
            return all_records[-limit:] if len(all_records) > limit else all_records
            
        except Exception as e:
            db_logger.error(f"Error getting leads: {str(e)}")
            return []

# Global instance
db_manager = None

def init_db_manager() -> GoogleSheetsManager:
    """Initialize global database manager."""
    global db_manager
    db_manager = GoogleSheetsManager()
    return db_manager

def get_db_manager() -> GoogleSheetsManager:
    """Get database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = init_db_manager()
    return db_manager
