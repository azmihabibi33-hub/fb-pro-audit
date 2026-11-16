#!/usr/bin/env python3
"""Cek satu caption Facebook Pro dari engagement bait — alat mandiri.

Penggunaan:
    python3 caption_check.py "Komen di bawah ya! Jangan lupa follow akun ini!"
    python3 caption_check.py --file caption.txt
    echo "caption..." | python3 caption_check.py

Keluar: daftar peringatan, atau "Aman" kalau bersih.
Kode keluar 0 = aman, 1 = ada peringatan.

Aturan (sama dengan fb_audit.py):
  - Kata kunci engagement bait: like, komentar/komen, share, bagikan,
    ikuti, hadir, menyala, klik link, cek bio, sub4sub.
  - "follow" HANYA dihitung kalau jelas ajakan (follow me/akun/dll);
    kata "follow" dalam kalimat biasa ("views don't always follow")
    bukan engagement bait.
  - Hashtag lebih dari 5 = peringatan.
"""

import argparse
import re
import sys

# (pola regex, label yang ditampilkan)
ENGAGEMENT_BAIT_KEYWORDS = [
    (r"\blike\b", "like"),
    (r"\bkomentar\b", "komentar"),
    (r"\bkomen\b", "komen"),
    (r"\bshare\b", "share"),
    (r"\bbagikan\b", "bagikan"),
    (r"follow\s+(me|aku|akun|dong|ya|yuk|dulu|@)", "follow"),
    (r"(jangan\s+lupa|yuk|ayo)\s+follow", "follow"),
    (r"\bikuti\b", "ikuti"),
    (r"\bhadir\b", "hadir"),
    (r"\bmenyala\b", "menyala"),
    (r"\bklik link\b", "klik link"),
    (r"\bcek bio\b", "cek bio"),
    (r"\bsub4sub\b", "sub4sub"),
]


def check_caption_policy(caption_text):
    """Mengecek apakah caption mengandung unsur engagement bait."""
    if not caption_text:
        return ["Peringatan: Caption kosong (kurang sinyal konteks untuk AI Meta)."]

    warnings = []
    text_lower = caption_text.lower()

    found_bait = sorted({label for pattern, label in ENGAGEMENT_BAIT_KEYWORDS
                         if re.search(pattern, text_lower)})
    if found_bait:
        warnings.append(
            f"Terdeteksi Engagement Bait: {', '.join(found_bait)}. "
            "Hindari ajakan eksplisit agar tidak kena shadowban.")

    hashtags = re.findall(r"#\w+", caption_text)
    if len(hashtags) > 5:
        warnings.append(
            f"Terlalu banyak hashtag ({len(hashtags)} tag). "
            "Gunakan maksimal 3-5 hashtag relevan.")

    return warnings if warnings else ["Aman: Caption bersih dari indikasi engagement bait."]


def main():
    parser = argparse.ArgumentParser(
        description="Cek satu caption dari engagement bait.")
    parser.add_argument("caption", nargs="*", help="Teks caption yang dicek")
    parser.add_argument("--file", help="Baca caption dari file")
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            caption = f.read()
    elif args.caption:
        caption = " ".join(args.caption)
    else:
        caption = sys.stdin.read()

    notes = check_caption_policy(caption.strip())
    for note in notes:
        print(f"  [Audit Teks] {note}")
    sys.exit(0 if notes[0].startswith("Aman") else 1)


if __name__ == "__main__":
    main()
