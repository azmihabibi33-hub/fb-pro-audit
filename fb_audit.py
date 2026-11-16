#!/usr/bin/env python3
"""Audit FB Pro — cek engagement bait di caption + metrik interaksi.

Memakai konektor facebook-cli (Muse) yang sudah terhubung ke akun user,
jadi TIDAK butuh User Access Token.

Penggunaan:
    FB_PROFILE_ID=100000015362821 python3 fb_audit.py
    python3 fb_audit.py --profile-id 100000015362821 --limit 5

Yang dicek per postingan (5 terbaru, sesuai --limit):
  1. Audit caption: kata kunci engagement bait + jumlah hashtag (>5 = peringatan)
  2. Interaksi: jumlah reaksi (like/love/dll) + jumlah komentar
  3. Video/Reel: dicatat bahwa views & retensi TIDAK tersedia via konektor

Yang TIDAK bisa diambil konektor (jujur dicatat, bukan dikarang):
  - jumlah share (tidak dikembalikan konektor)
  - views & retensi Reel profil pribadi — hanya dari dasbor FB Pro
    ("Lihat insight" di aplikasi/browser)

Perbaikan atas skrip Graph API asli (lihat reference/):
  - Skrip asli memakai host "https://facebook.com..." (salah, harus
    "graph.facebook.com") dan butuh User Access Token yang tidak ada.
  - Kata "follow" hanya dihitung kalau jelas ajakan (follow me/akun/dll);
    "views don't always follow" bukan engagement bait.
"""

import argparse
import json
import os
import re
import subprocess
import sys

FB_CLI = "/opt/hatch/bin/facebook-cli"

# (pola regex, label yang ditampilkan)
ENGAGEMENT_BAIT_KEYWORDS = [
    (r"\blike\b", "like"),
    (r"\bkomentar\b", "komentar"),
    (r"\bkomen\b", "komen"),
    (r"\bshare\b", "share"),
    (r"\bbagikan\b", "bagikan"),
    # "follow" HANYA kalau jelas ajakan — bukan kata "follow" dalam
    # kalimat Inggris biasa ("views don't always follow").
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


def cli(*args):
    out = subprocess.run([FB_CLI, *args], capture_output=True,
                         text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"facebook-cli gagal: {out.stderr.strip()}")
    return json.loads(out.stdout)


def run_checkup(profile_id, limit=5):
    print("=== MEMULAI AUDIT OTOMATIS AKUN FB PRO (via facebook-cli) ===\n")

    data = cli("timeline", "fetch", "--profile-id", profile_id,
               "--limit", str(limit))
    posts = data.get("posts", [])
    if not posts:
        print("Tidak ada postingan ditemukan.")
        return

    for idx, post in enumerate(posts, 1):
        post_id = post.get("post_id")
        caption = post.get("post_caption", "")
        created = post.get("post_created_at", {}).get("user_local", "")[:10]
        media = post.get("media_type", "")

        detail = cli("post", "read", "--post-id", post_id)
        comments = detail["posts"][0].get("comments", 0)

        rx = cli("post", "reactions", "read", "--post-id", post_id)
        likes = rx.get("summary", {}).get("total_count", 0)

        print(f"--- Postingan #{idx} ({created}) [{media}] ---")
        print(f"Caption : {caption[:60]}..." if len(caption) > 60
              else f"Caption : {caption}")

        # 1. Audit Kebijakan Caption
        for note in check_caption_policy(caption):
            print(f"  [Audit Teks] {note}")

        # 2. Audit Sinyal Interaksi Bermakna
        # Share TIDAK dikembalikan konektor -> rasio share tidak bisa dihitung.
        total_interaksi = likes + comments
        print(f"  [Interaksi] Like: {likes} | Komen: {comments} | "
              f"Share: tidak diketahui (konektor tidak mengembalikannya)")
        print(f"  [Interaksi] Total Like+Komen: {total_interaksi}")

        # 3. Audit Video / Reels (Jika postingan berupa video)
        if "video" in media:
            print("  [Metrik Video] Views & rata-rata tonton TIDAK tersedia "
                  "via konektor — cek lewat dasbor FB Pro "
                  "(\"Lihat insight\" di aplikasi/browser).")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Audit otomatis akun Facebook Pro.")
    parser.add_argument("--profile-id", default=os.environ.get("FB_PROFILE_ID"),
                        help="ID profil Facebook (atau env FB_PROFILE_ID)")
    parser.add_argument("--limit", type=int, default=5,
                        help="Jumlah postingan terbaru yang diaudit (default: 5)")
    args = parser.parse_args()

    if not args.profile_id:
        parser.error("ID profil wajib diisi: --profile-id atau env FB_PROFILE_ID")
    run_checkup(args.profile_id, args.limit)


if __name__ == "__main__":
    main()
