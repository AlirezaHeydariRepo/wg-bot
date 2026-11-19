import os
import re
import json
import urllib.request

# لینک‌های فیلترشده خودت را اینجا داخل گیومه بگذار
URLS = [
    ("WG-Zimmer", "https://www.wg-gesucht.de/wg-zimmer-in-Muenster.91.0.1.0.html"),
    ("1-Zimmer", "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Muenster.91.1.1.0.html#back_to_ad_14341674"),
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = "seen.json"

# خواندن لیست آگهی‌های قبلی
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen = set(json.load(f))
else:
    seen = set()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

new_found = False

for label, search_url in URLS:
    if not search_url.startswith("http"):
        continue
    try:
        req = urllib.request.Request(search_url, headers=headers)
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
        
        # پیدا کردن لینک تمام آگهی‌های صفحه
        matches = re.findall(r'href="((?:/en)?/[a-zA-Z0-9_-]+\.\d+\.html)"', html)
        
        # حذف لینک‌های تکراری در همان صفحه
        unique_paths = list(dict.fromkeys(matches))
        
        for path in unique_paths:
            if path not in seen:
                seen.add(path)
                new_found = True
                full_url = f"https://www.wg-gesucht.de{path}"
                msg = f"🏠 New {label} found:\n{full_url}"
                
                tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg}).encode("utf-8")
                urllib.request.urlopen(urllib.request.Request(tg_url, data=data), timeout=15)
                print(f"Sent: {full_url}")
    except Exception as e:
        print(f"Error checking {label}: {e}")

if new_found:
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f, indent=2)
