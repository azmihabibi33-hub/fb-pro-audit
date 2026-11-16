# FB Pro Audit — Gratis

Audit otomatis akun Facebook Pro — **gratis**, cek caption dari engagement
bait dan lihat metrik interaksi postingan terbaru. Dibuat untuk kreator FB Pro
yang mau tahu cepat apakah captionnya berisiko kena shadowban, tanpa buka
Graph API Explorer dan tanpa biaya apa pun.

## Isi repo

| File | Fungsi |
| --- | --- |
| `fb_audit.py` | Audit 5 postingan terbaru: audit caption, jumlah reaksi, jumlah komentar |
| `caption_check.py` | Cek satu caption saja (tempel teks → langsung verdict) |
| `reference/fb_audit_graphapi_original.py` | Skrip Graph API asli (referensi — **tidak bisa jalan apa adanya**, lihat di bawah) |

## Cara pakai

Butuh Python 3 dan konektor `facebook-cli` (Muse) yang sudah terhubung ke
akun Facebook. Tidak butuh User Access Token.

```bash
# Audit 5 postingan terbaru
FB_PROFILE_ID=100000015362821 python3 fb_audit.py

# Audit 10 postingan
python3 fb_audit.py --profile-id 100000015362821 --limit 10

# Cek satu caption
python3 caption_check.py "Komen di bawah ya! Jangan lupa follow akun ini!"
python3 caption_check.py --file caption.txt
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
