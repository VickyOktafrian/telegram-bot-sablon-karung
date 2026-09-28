# Struktur Google Sheet

Nama tab dan nama kolom harus **persis** seperti di bawah, karena workflow membacanya berdasarkan nama.

## Tab `User`

Daftar pengguna bot dan status persetujuannya.

| Kolom | Isi |
|---|---|
| `Telegram User ID` | ID angka akun Telegram |
| `Nama` | Nama depan di Telegram |
| `Role` | `Owner` atau `Pekerja` |
| `Status` | `Pending`, `Approved`, atau `Rejected` |
| `Didaftarkan/disetujui oleh (Telegram User ID Owner)` | ID Owner yang menyetujui |

Pengguna baru otomatis ditambahkan sebagai `Pekerja` dengan status `Pending`.

## Tab `Order`

Satu baris per order kerja.

| Kolom | Isi |
|---|---|
| `ID Order` | Format `ORD-001`, dibuat otomatis berurutan |
| `Jenis Karung` | Misalnya `UREA` |
| `Target Sablon` | Target bal sablon (0 jika tidak ada) |
| `Target Gosok` | Target bal gosok (0 jika tidak ada) |
| `Status` | `Aktif` atau `Selesai` |
| `Tanggal Dibuat` | Format `YYYY-MM-DD` (zona WITA) |

Aturan: satu jenis karung hanya boleh punya satu order `Aktif` pada satu waktu.

## Tab `Detail Log`

Satu baris per laporan kerja.

| Kolom | Isi |
|---|---|
| `Timestamp` | Waktu laporan (ISO, UTC). Dipakai juga sebagai pengenal baris saat ACC |
| `Order ID` | Mengacu ke `ID Order` |
| `Jenis Kerjaan` | `Sablon` atau `Gosok` |
| `Qty (bal)` | Jumlah bal |
| `Tukang` | Nama pelapor untuk sablon |
| `Helper` | Nama helper (opsional) |
| `Penggosok` | Nama pelapor untuk gosok |
| `Dilaporkan oleh (Telegram User ID)` | ID pelapor |
| `Status` | `Pending` (menunggu ACC) atau `Approved` |

Laporan yang ditolak Owner dihapus dari tab ini, sehingga target order kembali.

## Tab `Ringkasan`

Tab hitung otomatis (bukan ditulis bot). Isinya rekap per order: target, realisasi, dan sisa, dihitung dengan rumus dari tab `Detail Log`. Tulis rumus yang kamu pakai di sini agar orang lain bisa meniru.
