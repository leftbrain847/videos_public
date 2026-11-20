"""Open each video's fact sources and print their readable text, so a reviewer can check every claim (rubric G1).

python3 tools/fetch_sources.py s4_01_music_city_miracle [...]
Only fetches the https URLs listed in each video.json `sources`. Prints the page text between markers (also written to
out/sources/<id>.txt). The render workflow runs this on Actions, where the news and reference sites are reachable.
"""
import html.parser, json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = {"bytes": 3_000_000, "chars": 40_000, "timeout": 30}


class Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"}

    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in self.SKIP
        if tag in ("p", "br", "li", "h1", "h2", "h3", "tr", "div"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        self.skip -= tag in self.SKIP and self.skip > 0

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def page_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (fact-check script)"})
    with urllib.request.urlopen(req, timeout=LIMIT["timeout"]) as r:
        raw = r.read(LIMIT["bytes"]).decode(r.headers.get_content_charset() or "utf-8", "replace")
    p = Text(); p.feed(raw)
    return re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]+", " ", "".join(p.out))).strip()[: LIMIT["chars"]]


def main():
    out = ROOT / "football" / "out" / "sources"; out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for vid in sys.argv[1:]:
        S = json.loads((ROOT / "football" / "videos" / vid / "video.json").read_text())
        chunks = []
        for s in S.get("sources", []):
            url = s.get("url", "")
            if not url.startswith("https://"):
                continue
            try:
                body = page_text(url)
            except Exception as e:  # report and keep going: the reviewer needs to know which source failed
                body, bad = f"FETCH FAILED: {e}", bad + 1
            chunks.append(f"===== {vid} | {s.get('title', '')} | {url}\n{body}\n===== end {url}")
        text = "\n\n".join(chunks); (out / f"{vid}.txt").write_text(text); print(text)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
