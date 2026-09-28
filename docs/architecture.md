# Arsitektur dan Alur

Diagram di halaman ini memakai Mermaid, jadi tampil langsung di GitHub.

## 1. Pintu masuk: pesan atau tombol

Setiap update Telegram (pesan atau klik tombol) masuk lewat satu trigger, lalu dipisah menurut jenisnya.

```mermaid
flowchart TD
    A[Telegram Trigger] --> B{Klik tombol<br/>callback query?}
    B -->|ya| C[Parse callback data]
    C --> D{Jenis aksi}
    D -->|approve_user| D1[Update status user]
    D -->|confirm / pick| D2[Validasi ulang lalu simpan laporan]
    D -->|acc_laporan| D3[ACC atau tolak laporan]
    D -->|order| D4[Buat order final]
    D -->|aksi| D5[Jalankan usulan AI Owner]
    B -->|tidak, pesan biasa| E[Cek user di sheet User]
    E --> F{Sudah Approved?}
    F -->|belum terdaftar| G[Daftarkan sebagai Pending<br/>dan minta persetujuan Owner]
    F -->|Pending / Rejected| H[Balas status akun]
    F -->|Approved| I[Deteksi intent dengan LLM]
```

## 2. Pemilihan jalur setelah intent terdeteksi

```mermaid
flowchart TD
    I[AI: Deteksi Intent] --> P[Parse JSON]
    P --> O{Owner dan bukan<br/>intent kerja?}
    O -->|ya| Q[Asisten AI Owner<br/>tanya jawab + usulan ubah data]
    O -->|tidak| W{Pekerja dan bukan<br/>lapor?}
    W -->|ya| C[Asisten AI Pekerja<br/>hanya data miliknya]
    W -->|tidak| S{Switch intent}
    S --> L1[lapor_sablon / lapor_gosok]
    S --> L2[cek_progress]
    S --> L3[buat_order - khusus Owner]
    S --> L4[tutup_order - khusus Owner]
    S --> L5[approve_user - khusus Owner]
    S --> L6[tidak_jelas]
```

## 3. Alur laporan pekerja

Ini alur inti. Laporan tidak langsung dihitung, tetapi melewati konfirmasi pekerja dan persetujuan Owner.

```mermaid
sequenceDiagram
    participant P as Pekerja
    participant B as Bot (n8n)
    participant S as Google Sheets
    participant O as Owner

    P->>B: "8 bal urea sama ardi"
    B->>B: LLM mengekstrak jumlah, karung, helper
    B->>S: Baca Order dan Detail Log
    B->>B: Cocokkan ke order aktif, hitung sisa target
    alt beberapa order cocok
        B->>P: Pilih order (tombol)
        P->>B: Pilih salah satu
    end
    B->>P: Konfirmasi "Ya, benar / Batal"
    P->>B: Ya
    B->>S: Simpan laporan berstatus Pending
    B->>P: "Menunggu ACC Owner"
    B->>O: Notifikasi dengan tombol ACC / Tolak
    O->>B: ACC atau Tolak
    B->>S: Approved, atau hapus baris dan kembalikan target
    B->>P: Hasil dan sisa target terbaru
    B->>O: Konfirmasi hasil
```

## 4. Alur perubahan data lewat asisten AI Owner

AI tidak pernah menulis langsung. Ia hanya mengusulkan, dan kode yang memvalidasi serta mengeksekusi setelah konfirmasi.

```mermaid
flowchart LR
    Q[Owner: bebas mengetik] --> K[Susun konteks data<br/>Order, Ringkasan, Log, User]
    K --> AI[LLM menjawab atau mengusulkan aksi JSON]
    AI --> V{Usulan?}
    V -->|jawaban / pertanyaan balik| R[Balas ke Owner]
    V -->|usulan| C[Kode memvalidasi:<br/>kolom valid, baris unik,<br/>Role dan Owner terlindungi]
    C --> ST[Simpan sementara<br/>kedaluwarsa 30 menit]
    ST --> BTN[Tombol Ya / Batal]
    BTN -->|Ya| X[Google Sheets API<br/>tambah / ubah / hapus]
    BTN -->|Batal| Z[Tidak ada perubahan]
```

## Pembagian model LLM

| Tugas | Model | Alasan |
|---|---|---|
| Deteksi intent | `openai/gpt-oss-120b` | Klasifikasi dan ekstraksi harus akurat karena hasilnya menentukan jalur |
| Asisten Owner | `openai/gpt-oss-20b` | Butuh respons cepat untuk tanya jawab |
| Asisten Pekerja | `openai/gpt-oss-20b` | Obrolan singkat dengan konteks kecil |

Memori percakapan memakai window 6 pesan terakhir, dipisah per chat.
