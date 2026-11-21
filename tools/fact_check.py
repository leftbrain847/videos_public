"""Fact check (rubric G1): does each claim in a script appear in its sources? Prints no page text.

python3 tools/fact_check.py s4_01_music_city_miracle [...]      -> out/facts/<id>.json, exit 1 if any claim fails
Each video.json lists its claims: {"claim": "...", "terms": ["Dyson", "75|seventy-five", "yard"]}. A source supports a
claim when every term (alternatives split by |, case-insensitive) appears within WINDOW words of the others. A claim
passes when at least NEED sources support it. For each source the output is pass/fail, the URL and one snippet of at
most 15 words around the match, never more: the repo is public and the sources are copyrighted. A claim that fails is
rewritten or cut, never kept on memory.
"""
import html.parser, json, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = {"window": 40, "snippet_words": 15, "need": 2, "bytes": 3_000_000, "timeout": 30}


class Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in self.SKIP; self.out.append(" ")

    def handle_endtag(self, tag):
        self.skip -= tag in self.SKIP and self.skip > 0; self.out.append(" ")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


class HttpsOnly(urllib.request.HTTPRedirectHandler):
    """Follow redirects to https only (never http, file or anything else)."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith("https://"):
            raise urllib.error.HTTPError(newurl, code, "refused non-https redirect", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(HttpsOnly)
SPLIT = re.compile(r"[\s\-\u2010-\u2015/]+")   # pages and terms are split the same way, so "23-17" matches "23–17"


def page_words(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (fact-check script)"})
    with OPENER.open(req, timeout=CFG["timeout"]) as r:
        raw = r.read(CFG["bytes"]).decode(r.headers.get_content_charset() or "utf-8", "replace")
    p = Text(); p.feed(raw)
    return [w for w in SPLIT.split("".join(p.out)) if w]


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def same(word, term):
    """A page word matches a term word exactly, or by prefix for words of 4+ letters (timeout -> timeouts)."""
    return word == term or (len(term) >= 4 and not term.isdigit() and word.startswith(term))


def find(words, terms, window=CFG["window"]):
    """Index range of the tightest span holding every term, or None. A term may span words ("music city")."""
    nw = [norm(w) for w in words]
    hits = []
    for t in terms:
        alts = [[n for n in map(norm, SPLIT.split(a)) if n] for a in t.split("|")]
        pos = [i for i in range(len(nw)) for a in alts if a and all(same(nw[i + k] if i + k < len(nw) else "", x) for k, x in enumerate(a))]
        if not pos:
            return None
        hits.append(pos)
    best = None
    for start in hits[0]:
        span = [start]
        for pos in hits[1:]:
            near = min(pos, key=lambda p: abs(p - start)); span.append(near)
        lo, hi = min(span), max(span)
        if hi - lo <= window and (best is None or hi - lo < best[1] - best[0]):
            best = (lo, hi)
    return best


def snippet(words, span, n=CFG["snippet_words"]):
    lo, hi = span; mid = (lo + hi) // 2; a = max(0, min(mid - n // 2, len(words) - n))
    return " ".join(words[a:a + n])


def check(vid):
    S = json.loads((ROOT / "football" / "videos" / vid / "video.json").read_text())
    pages = {}
    for s in S.get("sources", []):
        u = s.get("url", "")
        if u.startswith("https://"):
            try:
                pages[u] = page_words(u)
            except Exception as e:  # a source that won't open supports nothing
                pages[u] = None; print(f"{vid}: could not open {u}: {e}")
    out = []
    for c in S.get("claims", []):
        per = []
        for u, words in pages.items():
            span = find(words, c["terms"]) if words else None
            per.append({"url": u, "pass": bool(span), "snippet": snippet(words, span) if span else ""})
        ok = sum(p["pass"] for p in per) >= CFG["need"]
        out.append({"claim": c["claim"], "pass": ok, "sources": per})
    return out, bool(S.get("claims"))


def main():
    d = ROOT / "football" / "out" / "facts"; d.mkdir(parents=True, exist_ok=True)
    bad = 0
    for vid in sys.argv[1:]:
        res, has = check(vid)
        if not has:
            print(f"FAIL {vid}: no claims listed"); bad += 1; continue
        (d / f"{vid}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
        for r in res:
            print(("PASS" if r["pass"] else "FAIL") + f" {vid}: {r['claim']}")
            for p in r["sources"]:
                print(f"     {'+' if p['pass'] else '-'} {p['url']}" + (f"  \"{p['snippet']}\"" if p["snippet"] else ""))
        bad += sum(not r["pass"] for r in res)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
