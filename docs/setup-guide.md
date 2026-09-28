# Panduan Pemasangan

## Prasyarat

- n8n yang bisa diakses lewat **HTTPS publik** (Telegram Trigger butuh alamat webhook publik). Kalau n8n dijalankan di rumah, Cloudflare Tunnel adalah cara yang praktis.
- Bot Telegram dari [@BotFather](https://t.me/BotFather).
- API key dari [GroqCloud](https://console.groq.com).
- Akun Google untuk Google Sheets (OAuth2).

## Langkah

### 1. Siapkan Google Sheet

1. Buat spreadsheet baru dengan **4 tab**: `User`, `Order`, `Detail Log`, `Ringkasan`.
2. Untuk `User`, `Order`, dan `Detail Log`, impor file CSV dari folder [`sheet-template/`](../sheet-template) (File → Impor → Sisipkan baris baru / Ganti sheet). Struktur kolom dijelaskan di [google-sheet-schema.md](google-sheet-schema.md).
3. Isi tab `Ringkasan` dengan rumus yang menghitung target, realisasi, dan sisa per order dari `Detail Log`.
4. Catat **ID spreadsheet** dari URL: `https://docs.google.com/spreadsheets/d/<INI_ID_NYA>/edit`.

### 2. Ganti placeholder di file workflow

Buka `workflow/bot-telegram-sablon-karung.json` di editor teks (misalnya VS Code), lalu gunakan Find & Replace:

| Cari | Ganti dengan |
|---|---|
| `YOUR_GOOGLE_SHEET_ID` | ID spreadsheet dari langkah 1 |
| `YOUR_TELEGRAM_BOT_TOKEN` | Token bot dari BotFather |

Placeholder token hanya ada di satu node, yaitu `HTTP: Kirim Pilihan Order`. Jangan commit file yang sudah diisi. Simpan salinan yang sudah terisi di luar repo.

### 3. Sesuaikan ID tab (gid)

Setiap tab Google Sheets punya `gid` (angka di URL setelah `#gid=`). Nilai di workflow adalah milik sheet asli, jadi ganti dengan milikmu:

| Tab | gid di workflow (contoh) |
|---|---|
| Order | `123405179` |
| User | `739012242` |
| Detail Log | `576316015` |
| Ringkasan | `1445525044` |

Cari dan ganti keempat angka itu dengan gid tab di spreadsheet-mu. Angka yang sama juga muncul di Code node `Code: Rencanakan Eksekusi` pada objek `GID`.

### 4. Impor ke n8n

Di n8n: **Workflows → Import from File**, pilih file JSON yang sudah diisi.

### 5. Buat kredensial

Buat tiga kredensial lalu pilih di node yang meminta:

1. **Telegram API**: isi token bot.
2. **Google Sheets OAuth2 API**: ikuti alur otorisasi Google di n8n.
3. **Groq API**: isi API key Groq.

Node `HTTP: Baca Sheet Target` dan `HTTP: Eksekusi Perubahan` memakai kredensial Google Sheets yang sama.

### 6. Daftarkan Owner pertama

Bot hanya menerima pengguna yang berstatus `Approved`, jadi Owner pertama dimasukkan manual. Tambahkan satu baris di tab `User`:

| Telegram User ID | Nama | Role | Status |
|---|---|---|---|
| (ID Telegram-mu) | (namamu) | Owner | Approved |

ID Telegram bisa didapat dari bot seperti [@userinfobot](https://t.me/userinfobot).

### 7. Aktifkan dan uji

1. Aktifkan workflow di n8n.
2. Kirim pesan ke bot dari akun lain. Bot mendaftarkannya sebagai `Pending`, dan Owner menerima tombol Terima/Tolak.
3. Buat order dari akun Owner: `bikin order karung urea 100 sablon 20 gosok`.
4. Dari akun pekerja yang sudah disetujui: `8 bal urea`.
5. Setujui laporan dari akun Owner, lalu cek tab `Detail Log`.
6. Tutup order: `selesaikan ORD-001`.

## Pemecahan Masalah

| Gejala | Kemungkinan penyebab |
|---|---|
| Bot tidak merespons sama sekali | Webhook tidak bisa dijangkau dari internet, atau workflow belum aktif |
| Tombol tidak berfungsi | Token pada node `HTTP: Kirim Pilihan Order` belum diganti |
| Error "Column to Match On" di node Sheets | Nama kolom di sheet tidak sama dengan yang ada di template |
| Model tidak ditemukan | Model Groq sudah dihentikan. Cek [daftar model aktif](https://console.groq.com/docs/models) dan ganti di node `Groq Chat Model`, `Groq Chat Model1`, dan `Groq Chat Model2` |
| Laporan ditolak "order tidak ditemukan" | Belum ada order berstatus `Aktif` untuk jenis karung itu |
