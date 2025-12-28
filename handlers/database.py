import gspread
import gspread_asyncio
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import asyncio
from config import GOOGLE_SHEETS_ID, CREDENTIALS_FILE, FAQ_TAB_NAME, LEADS_TAB_NAME, ANALYTICS_TAB_NAME
from utils.logger import db_logger

class GoogleSheetsManager:
    """Manager for Google Sheets integration with async support."""
    
    def __init__(self):
        """Initialize Google Sheets connection (sync fallback)."""
        try:
            self.scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate using service account (sync for backward compatibility)
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_FILE, 
                self.scope
            )
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            
            # Initialize async client manager
            self.async_manager = None
            self.async_client = None
            
            # Ticket number cache for performance
            self.last_ticket_number = 0
            self.ticket_cache_time = None
            
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
    
    def _get_creds(self):
        """Get credentials for async client."""
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped
    
    async def _get_async_client(self):
        """Get or create async gspread client."""
        if self.async_manager is None:
            self.async_manager = gspread_asyncio.AsyncioGspreadClientManager(self._get_creds)
        
        if self.async_client is None:
            self.async_client = await self.async_manager.authorize()
        
        return self.async_client
    
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
        """Get next ticket number (sync fallback for compatibility)."""
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            all_records = leads_sheet.get_all_records()
            if not all_records:
                return 1
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
    
    async def get_next_ticket_number_async(self) -> int:
        """
        Get next ticket number (async optimized with caching).
        
        Returns:
            Ticket number
        """
        try:
            # Check cache (valid for 5 seconds)
            if self.ticket_cache_time:
                time_diff = (datetime.now() - self.ticket_cache_time).total_seconds()
                if time_diff < 5 and self.last_ticket_number > 0:
                    new_number = self.last_ticket_number + 1
                    self.last_ticket_number = new_number
                    return new_number
            
            # Get async client
            client = await self._get_async_client()
            spreadsheet = await client.open_by_key(GOOGLE_SHEETS_ID)
            leads_sheet = await spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Optimize: Only get last 10 rows instead of all records
            # This drastically reduces API response time
            all_values = await leads_sheet.get_all_values()
            
            if len(all_values) <= 1:  # Only header or empty
                self.last_ticket_number = 1
                self.ticket_cache_time = datetime.now()
                return 1
            
            # Get last 10 rows (or all if less than 10)
            last_rows = all_values[-10:]
            max_number = 0
            
            # Ticket number is in column 2 (index 1)
            for row in last_rows:
                try:
                    if len(row) > 1:
                        ticket_num = int(row[1])
                        max_number = max(max_number, ticket_num)
                except:
                    pass
            
            new_number = max_number + 1
            self.last_ticket_number = new_number
            self.ticket_cache_time = datetime.now()
            
            return new_number
            
        except Exception as e:
            db_logger.error(f"Error getting next ticket number (async): {str(e)}")
            # Fallback: increment cache or start from 1
            if self.last_ticket_number > 0:
                return self.last_ticket_number + 1
            return 1
    
    def save_lead(self, discord_tag: str, name: str, order_id: str, 
                  issue_type: str, status: str = "PENDING") -> tuple:
        """
        Save lead data to Leads tab (DEPRECATED - use async version).
        
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
    
    async def save_lead_async(self, discord_tag: str, name: str, order_id: str, 
                              issue_type: str, status: str = "PENDING") -> tuple:
        """
        Save lead data to Leads tab (async optimized).
        
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
            # Get ticket number from cache first (faster)
            ticket_number = await self.get_next_ticket_number_async()
            
            # Get async client
            client = await self._get_async_client()
            spreadsheet = await client.open_by_key(GOOGLE_SHEETS_ID)
            leads_sheet = await spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Format timestamp
            tz = pytz.timezone('Asia/Jakarta')
            timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare data in order: timestamp, ticket_number, discord_tag, name, order_id, issue_type, status
            row_data = [timestamp, ticket_number, discord_tag, name, order_id, issue_type, status]
            
            # Append to sheet (async)
            await leads_sheet.append_row(row_data)
            
            # Log in background (non-blocking)
            asyncio.create_task(self._log_save_success(ticket_number, name, order_id))
            
            return (True, ticket_number)
            
        except Exception as e:
            db_logger.error(f"Error saving lead (async): {str(e)}")
            return (False, 0)
    
    async def _log_save_success(self, ticket_number: int, name: str, order_id: str):
        """Background task to log save success."""
        try:
            db_logger.info(f"New lead saved: #{ticket_number} {name} ({order_id})")
        except:
            pass
    
    def update_lead_status(self, order_id: str, new_status: str) -> bool:
        """
        Update lead status by order_id (DEPRECATED - use async version).
        
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
    
    async def update_lead_status_async(self, order_id: str, new_status: str) -> bool:
        """
        Update lead status by order_id (async optimized).
        
        Args:
            order_id: Order ID to update
            new_status: New status (PENDING, IN_PROGRESS, RESOLVED, CLOSED)
            
        Returns:
            True if successful, False if failed
        """
        try:
            # Get async client
            client = await self._get_async_client()
            spreadsheet = await client.open_by_key(GOOGLE_SHEETS_ID)
            leads_sheet = await spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Get all values (more efficient than get_all_records)
            all_values = await leads_sheet.get_all_values()
            
            if len(all_values) <= 1:  # Only header or empty
                db_logger.warning(f"Order ID {order_id} not found (empty sheet)")
                return False
            
            # Find row with order_id (order_id is column 5, index 4)
            for idx, row in enumerate(all_values[1:], start=2):  # Skip header
                if len(row) > 4 and str(row[4]).strip() == str(order_id).strip():
                    # Column 7 = status (index 6)
                    await leads_sheet.update_cell(idx, 7, new_status)
                    
                    # Log in background
                    asyncio.create_task(self._log_status_update(order_id, new_status))
                    return True
            
            db_logger.warning(f"Order ID {order_id} not found")
            return False
            
        except Exception as e:
            db_logger.error(f"Error updating lead status (async): {str(e)}")
            return False
    
    async def _log_status_update(self, order_id: str, new_status: str):
        """Background task to log status update."""
        try:
            db_logger.info(f"Lead status {order_id} updated to {new_status}")
        except:
            pass
    
    async def find_lead_by_order_id_async(self, order_id: str) -> dict:
        """
        Find specific lead by order_id (async optimized - no full table scan).
        
        Args:
            order_id: Order ID to find
            
        Returns:
            Lead record dict or None if not found
        """
        try:
            # Get async client
            client = await self._get_async_client()
            spreadsheet = await client.open_by_key(GOOGLE_SHEETS_ID)
            leads_sheet = await spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Find the cell containing the order_id (column 5)
            try:
                cell = await leads_sheet.find(str(order_id).strip())
                if cell and cell.col == 5:  # order_id is in column 5
                    # Get the entire row
                    row_values = await leads_sheet.row_values(cell.row)
                    
                    # Map to dict with column names
                    if len(row_values) >= 7:
                        return {
                            'timestamp': row_values[0] if len(row_values) > 0 else '',
                            'ticket_number': row_values[1] if len(row_values) > 1 else '',
                            'discord_tag': row_values[2] if len(row_values) > 2 else '',
                            'name': row_values[3] if len(row_values) > 3 else '',
                            'order_id': row_values[4] if len(row_values) > 4 else '',
                            'issue_type': row_values[5] if len(row_values) > 5 else '',
                            'status': row_values[6] if len(row_values) > 6 else '',
                        }
            except:
                # Cell not found
                pass
            
            return None
            
        except Exception as e:
            db_logger.error(f"Error finding lead by order_id (async): {str(e)}")
            return None
    
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
