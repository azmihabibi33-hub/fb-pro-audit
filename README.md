# FB Pro Audit — Gratis

Medical check-up buat akun Facebook Pro — **gratis**. Caption kalian dicek
otomatis: ada kata pemancing engagement (engagement bait) atau hashtag
kebanyakan, langsung ketahuan. Tidak perlu capek-capek tanya AI satu-satu
lagi soal kondisi konten kalian.

## Dua tool, dua cara pakai

| Tool | Buat apa | Butuh apa |
| --- | --- | --- |
| `caption_check.py` | Cek SATU caption | Python 3 saja — jalan di mana saja |
| `fb_audit.py` | Audit 5 postingan terbaru (caption + like + komen) | Akun Muse + Facebook terhubung ke Muse |

**Buat kreator lain:** kalau cuma mau cek caption, `caption_check.py` saja
sudah cukup — download, jalankan, tempel caption. Kalau mau audit lengkap
(postingan + like + komen otomatis), jalankan lewat Muse dengan Facebook
yang sudah terhubung.

## Cara pakai

### 1. Cek satu caption (di mana saja, cuma butuh Python 3)

```bash
python3 caption_check.py "Komen di bawah ya! Jangan lupa follow akun ini!"
python3 caption_check.py --file caption.txt
echo "caption..." | python3 caption_check.py
```

Hasil: daftar peringatan, atau "Aman" kalau bersih.
Kode keluar 0 = aman, 1 = ada peringatan.

### 2. Audit lengkap (di dalam Muse, Facebook sudah terhubung)

```bash
FB_PROFILE_ID=ISI_ID_PROFIL_ANDA python3 fb_audit.py
python3 fb_audit.py --profile-id ISI_ID_PROFIL_ANDA --limit 10
```

## Contoh hasil

```
--- Postingan #3 (2026-11-15) [entfbstatusupdatevideo] ---
  [Audit Teks] Terlalu banyak hashtag (6 tag). Gunakan maksimal 3-5 hashtag relevan.
  [Interaksi] Like: 5 | Komen: 1 | Share: tidak diketahui (konektor tidak mengembalikannya)
  [Interaksi] Total Like+Komen: 6
  [Metrik Video] Views & rata-rata tonton TIDAK tersedia via konektor
```

## Yang dicek

1. **Audit caption** — kata kunci engagement bait (`like`, `komen`,
   `share`, `bagikan`, `ikuti`, `hadir`, `menyala`, `klik link`,
   `cek bio`, `sub4sub`) dan hashtag lebih dari 5.
2. **Interaksi** — jumlah reaksi + jumlah komentar per postingan.

## Kejujuran soal batasan

- **Jumlah share tidak bisa diambil** — konektor tidak mengembalikannya,
  jadi rasio share tidak bisa dihitung.
- **Views & retensi Reel profil pribadi tidak tersedia via konektor.**
  Satu-satunya cara: dasbor FB Pro ("Lihat insight") di aplikasi/browser.
- **Kata "follow" hanya dihitung kalau jelas ajakan** (`follow me`,
  `follow akun`, `jangan lupa follow`). Kalimat Inggris biasa seperti
  *"views don't always follow"* bukan engagement bait — detektor lama
  sempat salah menandainya (false positive, diperbaiki 16 Nov 2026).

## Kenapa bukan Graph API langsung?

Skrip asli (`reference/fb_audit_graphapi_original.py`) punya 2 masalah:

1. Host API-nya salah: pakai `https://facebook.com...` padahal harus
   `https://graph.facebook.com`, dan URL-nya cacat (tanpa slash).
2. Butuh User Access Token (`user_posts` / `read_insights`) — dan insight
   video profil pribadi memang dibatasi Meta, jadi jalur itu tidak bisa
   diandalkan untuk akun profil.

Versi di repo ini memakai `facebook-cli` yang sudah terhubung, tanpa token.

## Lisensi

MIT — bebas dipakai dan diubah, bukan untuk dijual sebagai produk.
