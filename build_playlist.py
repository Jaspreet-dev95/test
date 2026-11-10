#!/usr/bin/env python3
"""Put CP24 first while preserving every channel in IPTV-org's main M3U."""
from pathlib import Path
import re
from urllib.request import Request, urlopen

SOURCE = "https://iptv-org.github.io/iptv/index.m3u"
DESTINATION = Path(__file__).resolve().parent / "cp24-first.m3u"


def main():
    request = Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 (compatible; CP24PlaylistUpdater/1.0)"})
    with urlopen(request, timeout=75) as response:
        text = response.read().decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("#EXTM3U"):
        raise RuntimeError("Source did not return a valid M3U playlist")

    header = []
    entries = []
    current = None
    for line in lines:
        if line.startswith("#EXTINF:"):
            current = [line]
            entries.append(current)
        elif current is None:
            header.append(line)
        else:
            current.append(line)

    if len(entries) < 100:
        raise RuntimeError(f"Source only contained {len(entries)} entries; refusing to replace playlist")

    cp24_idx = next(
        (i for i, entry in enumerate(entries)
         if re.search(r'tvg-id="CP24\.ca(?:@[^"]+)?"', entry[0], re.I)
         or re.search(r',CP24(?:\s*\([^)]*\))?\s*$', entry[0], re.I)),
        None,
    )
    if cp24_idx is None:
        raise RuntimeError("CP24 is not currently in the source; keeping existing playlist unchanged")

    first = entries.pop(cp24_idx)
    output = "".join(header + first + [line for entry in entries for line in entry])
    if not DESTINATION.exists() or DESTINATION.read_bytes() != output.encode("utf-8"):
        DESTINATION.write_bytes(output.encode("utf-8"))
    print(f"Updated {DESTINATION.name}: CP24 first, {len(entries) + 1} channels total")


if __name__ == "__main__":
    main()
