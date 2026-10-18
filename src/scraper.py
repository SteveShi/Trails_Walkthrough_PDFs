import os
import urllib.request
import urllib.error

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_url_cached(url: str, filename: str) -> str:
    filepath = os.path.join(CACHE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return content

def fetch_sora_1st_data():
    walkthrough_url = "https://trails-game.com/walkthrough/sora-1st/"
    notes_url = "https://trails-game.com/walkthrough/sora-1st-notes/"
    trophy_url = "https://trails-game.com/walkthrough/sora-1st-trophy/"
    
    wt = fetch_url_cached(walkthrough_url, "sora_1st_walkthrough.html")
    nt = fetch_url_cached(notes_url, "sora_1st_notes.html")
    tr = fetch_url_cached(trophy_url, "sora_1st_trophy.html")
    return wt, nt, tr
