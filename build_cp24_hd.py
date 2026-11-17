#!/usr/bin/env python3
"""Publish stable CP24 M3U with a fallback. No token renewal or scraping."""
import os
from pathlib import Path
from urllib.request import Request, urlopen

OUT = Path(__file__).with_name("cp24-hd-auto.m3u")
SD = "https://tvsen6.aynaott.com/cp24/index.m3u8"

def valid_hls(url):
    if not url.startswith("https://"):
        return False
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=20) as response:
            body = response.read(262144).decode("utf-8-sig", errors="replace")
        return body.startswith("#EXTM3U") and ("#EXTINF" in body or "#EXT-X-" in body)
    except Exception as e:
        print("HD check failed:", type(e).__name__)
        return False

url = os.environ.get("CP24_HD_URL", "").strip()
if url and valid_hls(url):
    label = "CP24 HD (unverified resolution)"
else:
    url = SD
    label = "CP24 (fallback 576p)"
content = "#EXTM3U\n" + '#EXTINF:-1 tvg-id="CP24.ca@SD" tvg-logo="https://i.imgur.com/YzjZUEl.png" group-title="News",' + label + "\n" + url + "\n"
OUT.write_text(content, encoding="utf-8")
print("Published", label)
