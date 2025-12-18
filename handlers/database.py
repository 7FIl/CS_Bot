import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from config import GOOGLE_SHEETS_ID, CREDENTIALS_FILE, FAQ_TAB_NAME, LEADS_TAB_NAME, ANALYTICS_TAB_NAME
from utils.logger import db_logger

class GoogleSheetsManager:
    """Manager untuk integrasi dengan Google Sheets."""
    
    def __init__(self):
        """Inisialisasi koneksi Google Sheets."""
        try:
            self.scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate menggunakan service account
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_FILE, 
                self.scope
            )
            self.client = gspread.authorize(credentials)
            
            # Buka spreadsheet
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            db_logger.info("Berhasil terhubung ke Google Sheets")
            
            # Cache FAQ data saat startup
            self.faq_cache = None
            self.reload_faq_cache()
            
        except FileNotFoundError:
            db_logger.error(f"File credentials '{CREDENTIALS_FILE}' tidak ditemukan!")
            raise
        except Exception as e:
            db_logger.error(f"Error saat menginisialisasi Google Sheets: {str(e)}")
            raise
    
    def reload_faq_cache(self):
        """Reload FAQ cache dari Sheets."""
        try:
            faq_sheet = self.spreadsheet.worksheet(FAQ_TAB_NAME)
            # Specify expected headers untuk menghindari duplicate header error
            self.faq_cache = faq_sheet.get_all_records(expected_headers=['trigger_id', 'button_label', 'response_text'])
            db_logger.info(f"FAQ cache di-reload. Total FAQ: {len(self.faq_cache)}")
        except Exception as e:
            db_logger.error(f"Error saat reload FAQ cache: {str(e)}")
            self.faq_cache = []
    
    def get_faq_data(self, refresh: bool = False) -> list:
        """
        Ambil data FAQ dari cache atau Sheets.
        
        Args:
            refresh: Jika True, refresh dari Sheets
            
        Returns:
            List of FAQ records
        """
        if refresh or self.faq_cache is None:
            self.reload_faq_cache()
        return self.faq_cache if self.faq_cache else []
    
    def find_faq_by_trigger(self, trigger_id: str) -> dict:
        """
        Cari FAQ berdasarkan trigger_id.
        
        Args:
            trigger_id: ID trigger button dari FAQ
            
        Returns:
            FAQ record atau None jika tidak ditemukan
        """
        faq_data = self.get_faq_data()
        for faq in faq_data:
            if str(faq.get('trigger_id', '')).strip().lower() == str(trigger_id).strip().lower():
                return faq
        return None
    
    def get_next_ticket_number(self) -> int:
        """
        Ambil nomor ticket berikutnya.
        
        Returns:
            Ticket number
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            all_records = leads_sheet.get_all_records()
            
            # Jika belum ada records, mulai dari 1
            if not all_records:
                return 1
            
            # Cari nomor tertinggi - gunakan 'ticket_number' sesuai header di sheet
            max_number = 0
            for record in all_records:
                try:
                    ticket_num = int(record.get('ticket_number', 0) or 0)
                    max_number = max(max_number, ticket_num)
                except:
                    pass
            
            return max_number + 1
            
        except Exception as e:
            db_logger.error(f"Error saat ambil next ticket number: {str(e)}")
            return 1
    
    def save_lead(self, discord_tag: str, name: str, order_id: str, 
                  issue_type: str, status: str = "PENDING") -> tuple:
        """
        Simpan data lead ke tab Leads.
        
        Args:
            discord_tag: Tag Discord user
            name: Nama user
            order_id: Order ID dari user
            issue_type: Tipe masalah
            status: Status ticket
            
        Returns:
            Tuple (success: bool, ticket_number: int)
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Ambil nomor ticket berikutnya
            ticket_number = self.get_next_ticket_number()
            
            # Format timestamp
            tz = pytz.timezone('Asia/Jakarta')
            timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            
            # Persiapkan data dengan urutan: timestamp, ticket_number, discord_tag, name, order_id, issue_type, status
            row_data = [timestamp, ticket_number, discord_tag, name, order_id, issue_type, status]
            
            # Append ke sheet
            leads_sheet.append_row(row_data)
            db_logger.info(f"Lead baru disimpan: #{ticket_number} {name} ({order_id})")
            return (True, ticket_number)
            
        except Exception as e:
            db_logger.error(f"Error saat menyimpan lead: {str(e)}")
            return (False, 0)
    
    def update_lead_status(self, order_id: str, new_status: str) -> bool:
        """
        Update status lead berdasarkan order_id.
        
        Args:
            order_id: Order ID untuk diupdate
            new_status: Status baru (PENDING, IN_PROGRESS, RESOLVED, CLOSED)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            
            # Cari row dengan order_id
            all_records = leads_sheet.get_all_records()
            for idx, record in enumerate(all_records, start=2):  # start=2 karena header di row 1
                if str(record.get('order_id', '')).strip() == str(order_id).strip():
                    # Column 7 = status (timestamp, ticket_number, discord_tag, name, order_id, issue_type, status)
                    leads_sheet.update_cell(idx, 7, new_status)
                    db_logger.info(f"Status lead {order_id} diupdate menjadi {new_status}")
                    return True
            
            db_logger.warning(f"Order ID {order_id} tidak ditemukan")
            return False
            
        except Exception as e:
            db_logger.error(f"Error saat update status lead: {str(e)}")
            return False
    
    def log_analytics(self, total_tickets: int, unresolved_queries: int) -> bool:
        """
        Catat data analytics.
        
        Args:
            total_tickets: Total tiket hari ini
            unresolved_queries: Total query yang belum selesai
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            analytics_sheet = self.spreadsheet.worksheet(ANALYTICS_TAB_NAME)
            
            date_str = datetime.now().strftime('%Y-%m-%d')
            row_data = [date_str, total_tickets, unresolved_queries]
            
            analytics_sheet.append_row(row_data)
            db_logger.info(f"Analytics data logged: {total_tickets} tickets, {unresolved_queries} unresolved")
            return True
            
        except Exception as e:
            db_logger.error(f"Error saat log analytics: {str(e)}")
            return False
    
    def get_all_leads(self, limit: int = 50) -> list:
        """
        Ambil data semua leads (untuk reporting).
        
        Args:
            limit: Jumlah maksimal records yang diambil
            
        Returns:
            List of lead records
        """
        try:
            leads_sheet = self.spreadsheet.worksheet(LEADS_TAB_NAME)
            all_records = leads_sheet.get_all_records()
            return all_records[-limit:] if len(all_records) > limit else all_records
            
        except Exception as e:
            db_logger.error(f"Error saat ambil leads: {str(e)}")
            return []

# Global instance
db_manager = None

def init_db_manager() -> GoogleSheetsManager:
    """Inisialisasi database manager global."""
    global db_manager
    db_manager = GoogleSheetsManager()
    return db_manager

def get_db_manager() -> GoogleSheetsManager:
    """Ambil instance database manager."""
    global db_manager
    if db_manager is None:
        db_manager = init_db_manager()
    return db_manager
