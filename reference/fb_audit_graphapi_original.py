import requests
import re

# ==========================================
# KONFIGURASI API (Ganti dengan data Anda)
# ==========================================
ACCESS_TOKEN = "MASUKKAN_USER_ACCESS_TOKEN_ANDA"
USER_ID = "me"  # Atau masukkan ID Profil FB Pro Anda

# Daftar kata kunci pemicu Engagement Bait & Spam
ENGAGEMENT_BAIT_KEYWORDS = [
    r"\blike\b", r"\bkomentar\b", r"\bkomen\b", r"\bshare\b",
    r"\bbagikan\b", r"\bfollow\b", r"\bikuti\b", r"\bhadir\b",
    r"\bmenyala\b", r"\bklik link\b", r"\bcek bio\b", r"\bsub4sub\b"
]

def check_caption_policy(caption_text):
    """Mengecek apakah caption mengandung unsur engagement bait."""
    if not caption_text:
        return ["Peringatan: Caption kosong (kurang sinyal konteks untuk AI Meta)."]

    warnings = []
    text_lower = caption_text.lower()

    # Cek kata kunci engagement bait
    found_bait = [kw.replace(r"\b", "") for kw in ENGAGEMENT_BAIT_KEYWORDS if re.search(kw, text_lower)]
    if found_bait:
        warnings.append(f"Terdeteksi Engagement Bait: {', '.join(found_bait)}. Hindari ajakan eksplisit agar tidak kena shadowban.")

    # Cek penggunaan hashtag berlebihan
    hashtags = re.findall(r"#\w+", caption_text)
    if len(hashtags) > 5:
        warnings.append(f"Terlalu banyak hashtag ({len(hashtags)} tag). Gunakan maksimal 3-5 hashtag relevan.")

    return warnings if warnings else ["Aman: Caption bersih dari indikasi engagement bait."]

def fetch_fb_pro_posts(limit=5):
    """Mengambil daftar postingan terbaru beserta metrik video/reels."""
    url = f"https://facebook.com{USER_ID}/posts"
    params = {
        "fields": "id,message,created_time,shares,comments.summary(true),likes.summary(true),attachments{type,media_type,target}",
        "limit": limit,
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()

def fetch_video_insights(video_id):
    """Mengambil metrik retensi & jangkauan video dari Graph API."""
    url = f"https://facebook.com{video_id}/video_insights"
    metrics = [
        "total_video_views",
        "total_video_avg_time_watched",
        "total_video_complete_views_30s",
        "total_video_impressions"
    ]
    params = {
        "metric": ",".join(metrics),
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = {}
    if "data" in data:
        for item in data["data"]:
            name = item.get("name")
            val = item.get("values", [{}])[0].get("value", 0)
            results[name] = val
    return results

def run_checkup():
    print("=== MEMULAI AUDIT OTOMATIS AKUN FB PRO ===\n")
    posts_data = fetch_fb_pro_posts(limit=5)

    if "error" in posts_data:
        print(f"[ERROR API]: {posts_data['error']['message']}")
        print("Pastikan Access Token valid dan memiliki izin (pages_read_engagement / user_posts / read_insights).")
        return

    posts = posts_data.get("data", [])
    if not posts:
        print("Tidak ada postingan ditemukan.")
        return

    for idx, post in enumerate(posts, 1):
        post_id = post.get("id")
        caption = post.get("message", "")
        created = post.get("created_time", "")

        likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
        comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
        shares = post.get("shares", {}).get("count", 0)

        print(f"--- Postingan #{idx} ({created[:10]}) ---")
        print(f"Caption : {caption[:60]}..." if len(caption) > 60 else f"Caption : {caption}")

        # 1. Audit Kebijakan Caption
        caption_audit = check_caption_policy(caption)
        for note in caption_audit:
            print(f"  [Audit Teks] {note}")

        # 2. Audit Sinyal Interaksi Bermakna
        total_interaksi = likes + comments + shares
        share_ratio = (shares / total_interaksi * 100) if total_interaksi > 0 else 0
        print(f"  [Interaksi] Like: {likes} | Komen: {comments} | Share: {shares} (Rasio Share: {share_ratio:.1f}%)")
        if share_ratio < 5 and total_interaksi > 10:
            print("  [Saran AI] Rasio Share rendah (<5%). Buat konten lebih relatable/edukatif agar memicu private share.")

        # 3. Audit Video / Reels (Jika postingan berupa video)
        attachments = post.get("attachments", {}).get("data", [])
        if attachments and attachments[0].get("media_type") == "video":
            video_id = attachments[0].get("target", {}).get("id")
            if video_id:
                v_metrics = fetch_video_insights(video_id)
                views = v_metrics.get("total_video_views", 0)
                avg_watch_ms = v_metrics.get("total_video_avg_time_watched", 0)
                avg_watch_sec = avg_watch_ms / 1000.0

                print(f"  [Metrik Video] Views: {views} | Rata-rata Tonton: {avg_watch_sec:.1f} detik")
                if avg_watch_sec < 3.0 and views > 0:
                    print("  [PERINGATAN RETENSI] Rata-rata tonton di bawah 3 detik! Perbaiki visual hook di 3 detik pertama.")
        print()

if __name__ == "__main__":
    run_checkup()
