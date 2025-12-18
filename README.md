# Discord Customer Support Bot 🤖

Kerangka kerja lengkap untuk membangun Discord Customer Support Bot yang terintegrasi dengan Google Sheets menggunakan Python.

## 📋 Fitur Utama

- ✅ **Menu Support Interaktif** - Buttons dan Modals yang user-friendly
- ✅ **Google Sheets Integration** - Database yang mudah dikelola admin
- ✅ **FAQ Management** - Kelola FAQ tanpa perlu coding
- ✅ **Ticket System** - Sistem eskalasi dengan Private Thread
- ✅ **Staff Notification** - Notifikasi real-time ke tim support
- ✅ **Analytics** - Tracking performa support
- ✅ **Logging System** - Audit trail lengkap semua aktivitas

## 🚀 Quick Start

### Prerequisite
- Python 3.10+
- Google Cloud Account (untuk Google Sheets API)
- Discord Server & Bot Token

### 1. Clone Repository
```bash
git clone <your-repo>
cd CS_Bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Google Cloud
Lihat `SETUP_GUIDE.md` untuk langkah-langkah detail setup Google Sheets API dan Service Account.

### 4. Konfigurasi Bot
```bash
# Copy .env.example ke .env
copy .env.example .env

# Edit .env dengan informasi Anda
```

### 5. Jalankan Bot
```bash
python main.py
```

## 📁 Struktur Folder

```
CS_Bot/
├── main.py                 # Entry point bot
├── config.py              # Konfigurasi utama
├── requirements.txt       # Python dependencies
├── .env.example          # Template environment variables
├── SETUP_GUIDE.md        # Panduan setup lengkap
├── README.md             # File ini
│
├── handlers/
│   ├── database.py       # Google Sheets manager
│   ├── commands.py       # Semua discord commands
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

| Command | Deskripsi | Permission |
|---------|-----------|-----------|
| `!support` | Buka menu support utama | Semua user |
| `!faq` | Tampilkan daftar FAQ | Semua user |
| `!reload` | Reload data dari Google Sheets | Admin |
| `!stats` | Tampilkan statistik support | Admin |

## 🔧 Struktur Google Sheets

### Tab 1: FAQ
Kelola pertanyaan yang sering diajakan

| trigger_id | button_label | response_text |
|-----------|--------------|---------------|
| pricing_1 | Berapa Harga? | Harga kami mulai dari Rp 50.000... |
| ship_1 | Pengiriman? | Kami kirim ke seluruh Indonesia... |

### Tab 2: Leads
Database semua ticket customer (auto-populated oleh bot)

| timestamp | discord_tag | name | order_id | issue_type | status |
|-----------|------------|------|----------|-----------|--------|
| 2024-12-18 10:30 | User#1234 | Budi | #12345 | Barang Belum Sampai | PENDING |

### Tab 3: Analytics
Data performa support (auto-logged oleh bot)

| date | total_tickets | unresolved_queries |
|------|---------------|------------------|
| 2024-12-18 | 15 | 3 |

## 🔐 Security

- ✅ Use environment variables untuk semua secrets
- ✅ Service Account credentials secure
- ✅ Rate limiting built-in
- ✅ Audit trail untuk semua aktivitas

## 📊 Workflow

### User Flow
```
1. User type !support atau klik support button
2. Tampil menu dengan 3 opsi: FAQ, Chat, Status
3. User pilih "Chat dengan Support"
4. Modal form muncul untuk isi data
5. Data disimpan ke Google Sheets
6. Staff diberitahu via notification channel
7. Staff ambil ticket → Private Thread dibuat
8. Percakapan terjadi di private thread
9. Staff tutup ticket → Status updated
```

### Admin Flow
```
1. Admin buka Google Sheets Tab FAQ
2. Edit/tambah FAQ tanpa perlu koding
3. Di Discord, admin ketik !reload
4. FAQ ter-update di bot
5. User bisa lihat FAQ baru via !faq
```

## 📈 Scalability

- Supports unlimited FAQ items
- Handles concurrent support requests
- Automatic daily log rotation
- Efficient Google Sheets caching
- Minimal API calls dengan smart caching

## 🐛 Troubleshooting

### Bot tidak respond
- Cek token di .env
- Cek Message Content Intent enabled
- Lihat logs di folder `logs/`

### Modal tidak muncul
```bash
pip install -U discord.py
```

### Google Sheets connection error
- Pastikan credentials.json ada
- Cek sheet sudah di-share ke service account email
- Lihat `SETUP_GUIDE.md` untuk detail

## 📝 Logging

Semua aktivitas dicatat di folder `logs/`:
- Daily log files: `bot_YYYY-MM-DD.log`
- Separate loggers untuk Database, Events, Bot
- Console output + File output

## 🤝 Contributing

Kontribusi welcome! Silakan:
1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Open Pull Request

## 📄 License

MIT License - Feel free to use for personal or commercial projects

## 📧 Support

Untuk masalah atau pertanyaan:
- Check `SETUP_GUIDE.md`
- Lihat logs di folder `logs/`
- Review code di `handlers/` folder

---

**Happy Coding! 🎉**

*Built with ❤️ using discord.py dan gspread*
