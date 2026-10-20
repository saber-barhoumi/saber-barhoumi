#!/usr/bin/env python3
"""
Generate assets/diagnostics.svg from LIVE GitHub data. Pure standard library.

    python scripts/generate_diagnostics.py                 # fetch from the GitHub API and write the SVG
    python scripts/generate_diagnostics.py --pending       # write the "awaiting first sync" placeholder
    python scripts/generate_diagnostics.py --from-json f   # render from a saved JSON (testing only)

Environment:
    GH_USER         GitHub login (default: saber-barhoumi)
    GITHUB_TOKEN    provided automatically inside GitHub Actions (public repo data + rate limit)
    PROFILE_TOKEN   OPTIONAL personal access token. Only needed for the "contributions (12 months)" tile
                    and heat strip, because GitHub's GraphQL contribution data is user-scoped.
                    Without it the tile shows n/a. Everything else still works.

Nothing is hardcoded: if the API fails the existing SVG is left untouched.
"""
import argparse, datetime as dt, json, os, sys, urllib.error, urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "diagnostics.svg")
USER = os.environ.get("GH_USER", "saber-barhoumi")
CYAN, BLUE, GREEN, PURPLE, TEXT, DIM, LINE = "#00e5ff", "#2979ff", "#39ff96", "#9d5cff", "#d6e6f5", "#7f97b3", "#14324d"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
W, H = 800, 430


def api(path, token=None, data=None):
    req = urllib.request.Request("https://api.github.com" + path if path.startswith("/") else path,
                                 data=json.dumps(data).encode() if data else None)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "saber-profile-diagnostics")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    ptoken = os.environ.get("PROFILE_TOKEN") or token
    user = api(f"/users/{USER}", token)
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}", token)
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]
    langs = {}
    for r in own:
        try:
            for k, v in api(f"/repos/{USER}/{r['name']}/languages", token).items():
                langs[k] = langs.get(k, 0) + v
        except Exception as ex:  # one repo failing must not break the panel
            print("languages skipped for", r["name"], ex, file=sys.stderr)
    contrib = None
    try:
        since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=364)).strftime("%Y-%m-%dT00:00:00Z")
        q = ('query($login:String!,$from:DateTime!){user(login:$login){contributionsCollection(from:$from){'
             'totalCommitContributions totalPullRequestContributions '
             'contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}')
        res = api("/graphql", ptoken, {"query": q, "variables": {"login": USER, "from": since}})
        cc = res["data"]["user"]["contributionsCollection"]
        days = [d["contributionCount"] for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
        contrib = {"total": cc["contributionCalendar"]["totalContributions"], "commits": cc["totalCommitContributions"],
                   "prs": cc["totalPullRequestContributions"], "days": days}
    except Exception as ex:
        print("contributions unavailable (set PROFILE_TOKEN to enable):", ex, file=sys.stderr)
    return {
        "login": USER, "public_repos": user["public_repos"], "followers": user["followers"],
        "stars": sum(r["stargazers_count"] for r in own), "languages": langs,
        "last_push": max((r["pushed_at"] for r in own if r.get("pushed_at")), default=None),
        "contrib": contrib, "synced": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def t(x, y, s, txt, fill=TEXT, w="normal", a="start"):
    return f'<text x="{x}" y="{y}" font-size="{s}" fill="{fill}" font-weight="{w}" text-anchor="{a}">{escape(str(txt))}</text>'


def render(d):
    pending = d is None
    g = []
    g.append(f'<rect width="{W}" height="{H}" rx="10" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="10" fill="url(#grid)"/>'
             f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{LINE}"/>')
    g.append(t(32, 40, 14, "$ ./system-status.sh --live", GREEN, "bold"))
    g.append(t(W - 32, 40, 12, "AWAITING FIRST SYNC" if pending else f"last sync: {d['synced']}", PURPLE if pending else DIM, a="end"))
    c = d["contrib"] if d else None
    tiles = [("PUBLIC REPOS", "—" if pending else d["public_repos"]), ("STARS EARNED", "—" if pending else d["stars"]),
             ("FOLLOWERS", "—" if pending else d["followers"]),
             ("CONTRIBUTIONS · 12M", "—" if pending else (c["total"] if c else "n/a"))]
    tw = (W - 64 - 36) // 4
    for i, (lab, val) in enumerate(tiles):
        x = 32 + i * (tw + 12)
        g.append(f'<rect x="{x}" y="58" width="{tw}" height="78" rx="8" fill="#08111f" stroke="{CYAN}55"/>')
        g.append(t(x + 14, 100, 34, val, CYAN, "bold") + t(x + 14, 123, 12, lab, TEXT))
    g.append(t(32, 168, 13, "// LANGUAGE TELEMETRY (bytes across public, non-fork repos)", DIM))
    cols = [CYAN, BLUE, PURPLE, GREEN, "#5ad1ff", "#b99cff"]
    if pending:
        g.append(t(32, 200, 14, "Run the “Update profile diagnostics” workflow once (Actions tab) to populate this panel.", TEXT))
    else:
        total = sum(d["languages"].values()) or 1
        top = sorted(d["languages"].items(), key=lambda kv: -kv[1])[:6]
        x = 32
        for i, (k, v) in enumerate(top):
            w = (W - 64) * v / total
            g.append(f'<rect x="{x:.1f}" y="180" width="{max(w-2,1):.1f}" height="16" rx="3" fill="{cols[i]}" opacity=".9"/>')
            x += w
        for i, (k, v) in enumerate(top):
            cx = 32 + (i % 3) * 250
            cy = 226 + (i // 3) * 22
            g.append(f'<rect x="{cx}" y="{cy-10}" width="11" height="11" rx="2" fill="{cols[i]}"/>' + t(cx + 18, cy, 13, f"{k}  {100*v/total:.1f}%", TEXT))
    g.append(t(32, 292, 13, "// CONTRIBUTION ACTIVITY (last 26 weeks)", DIM))
    if c and c["days"]:
        days = c["days"][-182:]
        mx = max(days) or 1
        for i, n in enumerate(days):
            wk, dow = divmod(i, 7)
            op = 0.12 if n == 0 else 0.3 + 0.7 * min(n / mx, 1)
            g.append(f'<rect x="{32 + wk*29.2:.1f}" y="{304 + dow*14}" width="24" height="11" rx="2" fill="{CYAN}" opacity="{op:.2f}"/>')
        g.append(t(32, 418, 12, f"{c['commits']} commits · {c['prs']} pull requests in the last 12 months", DIM))
    else:
        g.append(t(32, 330, 13, "n/a — optional PROFILE_TOKEN secret not set" if not pending else "—", DIM))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">GitHub system diagnostics for {escape(USER)}</title><desc id="d">Live telemetry generated by a GitHub Action: public repositories, stars, followers, contributions and language distribution.</desc>
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04070d"/><stop offset="1" stop-color="#0a1424"/></linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{CYAN}" stroke-opacity=".07"/></pattern></defs>
<style>text{{font-family:{FONT}}}</style>
{chr(10).join(g)}
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--from-json")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    if a.pending:
        data = None
    elif a.from_json:
        data = json.load(open(a.from_json))
    else:
        try:
            data = fetch()
        except (urllib.error.URLError, KeyError, ValueError) as ex:
            print("GitHub API unavailable — leaving existing diagnostics.svg untouched:", ex, file=sys.stderr)
            return 0
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render(data))
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
