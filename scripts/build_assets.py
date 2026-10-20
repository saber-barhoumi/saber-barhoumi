#!/usr/bin/env python3
"""
Generate every static SVG used by README.md (SABER://DIGITAL-WORLD).

    python scripts/build_assets.py

Pure standard library. Run scripts/build_portrait.py first (hero.svg embeds its JPEG output).
All SVGs are self-contained: no scripts, no external fonts, no remote images, so they render
inside GitHub's <img> sandbox. Animations are plain CSS keyframes and are disabled automatically
for visitors who prefer reduced motion. Every element is fully visible in its default state.
"""
import base64, json, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
ICONS = json.load(open(os.path.join(HERE, "icons.json")))["icons"]

BG0, BG1, PANEL, LINE = "#04070d", "#0a1424", "#0b1628", "#14324d"
CYAN, BLUE, GREEN, PURPLE = "#00e5ff", "#2979ff", "#39ff96", "#9d5cff"
TEXT, DIM = "#d6e6f5", "#7f97b3"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
W = 800


def e(s):
    return escape(str(s))


def svg(w, h, body, title, desc=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
<title id="t">{e(title)}</title><desc id="d">{e(desc or title)}</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".25" stop-color="{CYAN}"/><stop offset=".75" stop-color="{BLUE}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{CYAN}" stroke-opacity=".07"/></pattern>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
text{{font-family:{FONT}}}
.fade{{animation:fade .7s ease-out both}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.glitch{{animation:glitch 6s infinite}}
@keyframes glitch{{0%,90%,100%{{transform:translate(0,0)}}92%{{transform:translate(-4px,1px)}}94%{{transform:translate(4px,-1px)}}96%{{transform:translate(-2px,0)}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
.scan{{animation:scan 5s linear infinite}}
@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY(var(--sh,300px))}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
{body}
</svg>
'''


def T(x, y, s, txt, fill=TEXT, weight="normal", anchor="start", cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{s}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"{c} {extra}>{e(txt)}</text>'


def bg(w, h, grid=True):
    out = f'<rect width="{w}" height="{h}" rx="10" fill="url(#bg)"/>'
    if grid:
        out += f'<rect width="{w}" height="{h}" rx="10" fill="url(#grid)"/>'
    out += f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="none" stroke="{LINE}"/>'
    return out


def brackets(x, y, w, h, c=CYAN, ln=16, sw=2):
    p = ""
    for (px, py, sx, sy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
        p += f'<path d="M{px+sx*ln} {py}H{px}V{py+sy*ln}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
    return p


def icon(slug, x, y, size=22, fill=TEXT, op=1):
    return (f'<path transform="translate({x} {y}) scale({size/24:.4f})" d="{ICONS[slug]}" fill="{fill}" opacity="{op}"/>')


def panel(x, y, w, h, stroke=LINE, fill=PANEL, rx=8, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"{d}/>'


def save(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name:28s}{os.path.getsize(path)/1024:7.1f} KB")


# ───────────────────────────── header ─────────────────────────────
def header():
    h = 250
    b = bg(W, h)
    b += brackets(14, 14, W - 28, h - 28)
    b += T(34, 40, 13, "SYS://ONLINE", GREEN, "bold", cls="pulse")
    b += T(W - 34, 40, 13, "SABER-OS v2026.10", DIM, anchor="end")
    # glitch title: purple + cyan ghost layers, white core
    for dx, col, op, cls in [(-3, PURPLE, .55, "glitch"), (3, CYAN, .45, "glitch"), (0, "#ffffff", 1, "")]:
        b += T(W / 2 + dx, 106, 45, "SABER://DIGITAL-WORLD", col, "bold", "middle", cls, f'opacity="{op}"')
    b += f'<rect x="120" y="122" width="{W-240}" height="2" fill="url(#neon)"/>'
    b += T(W / 2, 152, 17, "full-stack · microservices · AI/ML", CYAN, anchor="middle")
    boot = [("[ OK ]", "mounting /projects/xpark-gmao"), ("[ OK ]", "mounting /projects/cryptovisionai"),
            ("[ OK ]", "loading skills.sys"), (">", "session ready")]
    for i, (a, t) in enumerate(boot):
        y = 184 + i * 17
        d = f'style="animation-delay:{0.4+i*0.55}s"'
        b += f'<g class="fade" {d}>{T(40, y, 13.5, a, GREEN, "bold")}{T(98 if a!=">" else 62, y, 13.5, t, TEXT)}</g>'
        if a == ">":
            b += f'<rect class="blink" x="{62+len(t)*8.1+4:.0f}" y="{y-11}" width="8" height="14" fill="{CYAN}"/>'
    b += T(W - 40, 236, 12, "scroll ↓ to enter the workspace", DIM, anchor="end")
    save("header.svg", svg(W, h, b, "SABER://DIGITAL-WORLD",
         "Animated terminal-style banner for the GitHub profile of Saber Barhoumi."))


# ───────────────────────────── hero ─────────────────────────────
def hero():
    h = 394
    jpg = base64.b64encode(open(os.path.join(HERE, "source", "portrait-frame-embed.jpg"), "rb").read()).decode()
    pw, ph = 300, 347
    b = bg(W, h)
    b += f'<defs><clipPath id="pc"><rect x="20" y="24" width="{pw}" height="{ph}"/></clipPath></defs>'
    b += f'<image x="20" y="24" width="{pw}" height="{ph}" xlink:href="data:image/jpeg;base64,{jpg}" preserveAspectRatio="xMidYMid slice"/>'
    b += (f'<g clip-path="url(#pc)"><rect class="scan" style="--sh:{ph}px" x="20" y="24" width="{pw}" height="3" fill="{CYAN}" opacity=".30"/></g>')
    # terminal window
    tx, ty, tw, th = 345, 24, 435, 347
    b += panel(tx, ty, tw, th, stroke=CYAN + "55", fill="#060d19")
    b += f'<path d="M{tx} {ty+8}a8 8 0 0 1 8-8h{tw-16}a8 8 0 0 1 8 8V{ty+34}H{tx}z" fill="#0d1d33"/>'
    for i, c in enumerate(["#ff5f56", "#ffbd2e", GREEN]):
        b += f'<circle cx="{tx+20+i*18}" cy="{ty+17}" r="5" fill="{c}" opacity=".85"/>'
    b += T(tx + tw / 2, ty + 22, 13, "saber@digital-world: ~", DIM, anchor="middle")
    L = tx + 22
    V = L + 92
    y = ty + 64
    step = 26
    rows = [
        ("cmd", "whoami"),
        ("kv", "Name", "Saber Barhoumi"),
        ("kv", "Handle", "@saber-barhoumi"),
        ("kv", "Role", "Full-Stack Developer"),
        ("kv", "Focus", "Microservices · AI/ML · Cloud"),
        ("kv", "Project", "XPARK GMAO (graduation)"),
        ("cmd", "./status.sh"),
        ("ok", "xpark-gmao", "flagship"),
        ("ok", "cryptovisionai", "featured"),
        ("cur",),
    ]
    for i, r in enumerate(rows):
        yy = y + i * step
        d = f'style="animation-delay:{0.3+i*0.45}s"'
        if r[0] == "cmd":
            g = T(L, yy, 16.5, "$", GREEN, "bold") + T(L + 18, yy, 16.5, r[1], CYAN, "bold")
        elif r[0] == "kv":
            g = T(L, yy, 16, r[1], DIM) + T(V, yy, 16, r[2], "#ffffff", "bold")
        elif r[0] == "ok":
            g = T(L, yy, 15, "[ OK ]", GREEN, "bold") + T(L + 66, yy, 15, r[1], TEXT) + T(tx + tw - 22, yy, 15, r[2], PURPLE, "bold", "end")
        else:
            g = T(L, yy, 16.5, "$", GREEN, "bold") + f'<rect class="blink" x="{L+18}" y="{yy-13}" width="9" height="16" fill="{CYAN}"/>'
        b += f'<g class="fade" {d}>{g}</g>'
    b += brackets(tx - 6, ty - 6, tw + 12, th + 12, PURPLE, 14, 2)
    save("hero.svg", svg(W, h, b, "Saber Barhoumi — digital identity",
         "Portrait of Saber Barhoumi in a neon HUD frame beside a terminal showing: name, handle, role Full-Stack Developer, focus areas and featured projects."))


# ───────────────────────────── banners / divider / footer ─────────────────────────────
def banner(name, num, cmd, tag):
    h = 56
    b = f'<rect width="{W}" height="{h}" rx="8" fill="#060d19" stroke="{LINE}"/>'
    b += f'<rect x="0" y="0" width="5" height="{h}" rx="2" fill="{CYAN}"/>'
    b += T(24, 35, 17, "saber@digital-world:~$", GREEN, "bold")
    b += T(24 + 23 * 10.2 + 8, 35, 17, cmd, CYAN, "bold")
    b += T(W - 20, 35, 13, tag, DIM, anchor="end")
    b += f'<rect x="{W-86}" y="14" width="0" height="0"/>'
    b += f'<rect x="24" y="{h-4}" width="{W-48}" height="1.5" fill="url(#neon)" opacity=".7"/>'
    save(name, svg(W, h, b, f"{num} {cmd}", f"Terminal prompt: {cmd}"))


def divider():
    b = f'<rect x="0" y="7" width="{W}" height="2" fill="url(#neon)"/><rect x="{W/2-6}" y="3" width="12" height="10" fill="{CYAN}" filter="url(#glow)" transform="rotate(45 {W/2} 8)"/>'
    save("divider.svg", svg(W, 16, b, "divider"))


def footer():
    h = 168
    b = bg(W, h)
    b += T(32, 44, 16, "saber@digital-world:~$", GREEN, "bold") + T(32 + 23 * 9.9 + 8, 44, 16, "exit", CYAN, "bold")
    for i, (t, c) in enumerate([("logout", DIM), ("[ session closed ] thanks for visiting the digital world.", TEXT),
                                ("Connection to digital-world closed.", DIM)]):
        b += f'<g class="fade" style="animation-delay:{0.5+i*0.6}s">{T(32, 76+i*24, 15, t, c)}</g>'
    b += T(32, 76 + 3 * 24 + 6, 16, "$", GREEN, "bold") + f'<rect class="blink" x="50" y="{76+3*24-8}" width="9" height="16" fill="{CYAN}"/>'
    b += f'<rect x="32" y="{h-22}" width="{W-64}" height="2" fill="url(#neon)"/>'
    b += T(W - 32, 44, 12, "SABER://DIGITAL-WORLD", DIM, anchor="end")
    save("footer.svg", svg(W, h, b, "Session closed", "Terminal footer: exit, session closed, connection closed."))


# ───────────────────────────── tech universe ─────────────────────────────
def chip(x, y, w, label, slug=None, dim=False, accent=CYAN):
    st = DIM if dim else TEXT
    p = panel(x, y, w, 36, stroke=(LINE if dim else accent + "66"), fill="#08111f", rx=6, dash=("3 3" if dim else ""))
    if slug:
        p += icon(slug, x + 8, y + 8, 20, st, .55 if dim else 1)
    else:
        p += f'<path d="M{x+18} {y+11}l6.5 3.7v7.6l-6.5 3.7l-6.5-3.7v-7.6z" fill="none" stroke="{st}" stroke-width="1.5" opacity="{.55 if dim else .9}"/>'
    avail = w - 36 - 4
    size = min(13, avail / (0.602 * max(len(label), 1)))  # monospace advance is ~0.6em
    p += T(x + 34, y + 23, round(size, 1), label, st)
    return p


def tech():
    cols, pw, gap = 2, 376, 16
    cats = [
        ("01", "FRONTEND ENGINEERING", CYAN, [("React", "react"), ("TypeScript", "typescript"), ("Next.js", "nextdotjs"), ("Angular", "angular"),
                                               ("Vite", "vite"), ("Expo / RN", "expo"), ("Leaflet", "leaflet"), ("Sass", "sass")], []),
        ("02", "BACKEND ENGINEERING", BLUE, [(".NET 8", "dotnet"), ("Spring Boot", "springboot"), ("Express", "express"), ("FastAPI", "fastapi"),
                                              ("Symfony", "symfony"), ("Prisma", "prisma")], []),
        ("03", "DATABASES & MESSAGING", CYAN, [("PostgreSQL", "postgresql"), ("MongoDB", "mongodb"), ("RabbitMQ", "rabbitmq"), ("Qdrant", "qdrant"),
                                                ("EF Core", None), ("SignalR", None)], []),
        ("04", "AI & MACHINE LEARNING", PURPLE, [("Python", "python"), ("TensorFlow", "tensorflow"), ("PyTorch", "pytorch"), ("scikit-learn", "scikitlearn"),
                                                  ("XGBoost", None), ("OpenCV", "opencv"), ("pandas", "pandas"), ("Ollama", "ollama"), ("RAG", None)], []),
        ("05", "DEVOPS & INFRA", BLUE, [("Docker", "docker"), ("Compose", "docker"), ("Nginx", "nginx")],
         [("Kubernetes", "kubernetes"), ("Jenkins", "jenkins"), ("Keycloak", "keycloak"), ("Kafka", "apachekafka"), ("AWS", None)]),
        ("06", "DEVELOPMENT TOOLS", CYAN, [("Git", "git"), ("GitHub", "github"), ("Swagger", "swagger"), ("Power BI", None), ("Miro", "miro")], []),
    ]
    cw = (pw - 24 - 12) // 3
    rows_h = []
    for _, _, _, v, d in cats:
        n = (len(v) + 2) // 3 + ((len(d) + 2) // 3 if d else 0)
        rows_h.append(54 + n * 44 + (22 if d else 0) + 8)
    layout, y0 = [], 0
    for r in range(3):
        hh = max(rows_h[r * 2], rows_h[r * 2 + 1])
        layout.append((y0, hh))
        y0 += hh + 20
    H = y0 - 20 + 56
    b = bg(W, H, grid=True)
    b += T(32, 34, 14, "$ ./tech-stack.sh --verified", GREEN, "bold") + T(W - 32, 34, 12, "dashed = in training (not yet used in a public repo)", DIM, anchor="end")
    for idx, (num, name, acc, verified, training) in enumerate(cats):
        r, c = divmod(idx, 2)
        top, hh = layout[r]
        x = 16 + c * (pw + gap)
        y = 52 + top
        b += panel(x, y, pw, hh, stroke=acc + "55", fill="#070f1c")
        b += brackets(x, y, pw, hh, acc, 12, 2)
        b += T(x + 18, y + 28, 15, f"[{num}]", acc, "bold") + T(x + 62, y + 28, 15, name, "#ffffff", "bold")
        b += f'<rect x="{x+16}" y="{y+38}" width="{pw-32}" height="1" fill="{acc}" opacity=".35"/>'
        for i, (lab, slug) in enumerate(verified):
            rr, cc = divmod(i, 3)
            b += chip(x + 12 + cc * (cw + 6), y + 50 + rr * 44, cw, lab, slug, accent=acc)
        if training:
            base_y = y + 50 + ((len(verified) + 2) // 3) * 44
            b += T(x + 18, base_y + 12, 12, "IN TRAINING", PURPLE, "bold")
            for i, (lab, slug) in enumerate(training):
                rr, cc = divmod(i, 3)
                b += chip(x + 12 + cc * (cw + 6), base_y + 20 + rr * 44, cw, lab, slug, dim=True)
    save("tech-universe.svg", svg(W, H, b, "Technical universe",
         "Technologies grouped by category: frontend, backend, databases and messaging, AI and machine learning, DevOps, tools. Items marked in training are skills being learned."))


# ───────────────────────────── XPARK ─────────────────────────────
def xpark_panel():
    h = 604
    b = bg(W, h)
    b += brackets(10, 10, W - 20, h - 20, CYAN, 18, 3)
    b += T(32, 44, 14, "FLAGSHIP PROJECT // GRADUATION PROJECT", PURPLE, "bold")
    b += T(32, 82, 36, "XPARK GMAO", "#ffffff", "bold", extra='filter="url(#glow)"')
    b += T(32, 108, 15, "fleet · mission · maintenance management for transport operations", CYAN)
    tiles = [("8", ".NET 8 microservices"), ("4", "Python AI services"), ("3", "client apps"), ("20", "compose services")]
    tw = (W - 64 - 3 * 12) // 4
    for i, (n, l) in enumerate(tiles):
        x = 32 + i * (tw + 12)
        b += panel(x, 128, tw, 74, stroke=CYAN + "55", fill="#08111f")
        b += T(x + 14, 168, 36, n, CYAN, "bold") + T(x + 14, 190, 12.5, l, TEXT)
    b += T(32, 232, 13, "// BACKEND — Clean Architecture: API → Application → Domain ← Infrastructure", DIM)
    svcs = [("IAM", "JWT · MFA · users", "5001"), ("FLEET", "vehicles · fuel · documents", "5002"), ("MISSION", "missions · quotes · GPS tracking", "5003"),
            ("MAINTENANCE", "work orders · spare parts", "5004"), ("FINANCE", "invoices · fuel costs", "5005"), ("ALERTS", "system notifications", "5006"),
            ("CHAT", "real-time chat (SignalR)", "5007"), ("PREDICTION", "rule-based risk engine", "5009")]
    sw = (W - 64 - 3 * 12) // 4
    for i, (n, d, p) in enumerate(svcs):
        r, c = divmod(i, 4)
        x, y = 32 + c * (sw + 12), 244 + r * 86
        b += panel(x, y, sw, 76, stroke=BLUE + "88", fill="#08111f")
        b += f'<circle cx="{x+15}" cy="{y+19}" r="4" fill="{GREEN}" class="pulse" style="animation-delay:{i*0.3}s"/>'
        b += T(x + 27, y + 24, 13.5, n, "#ffffff", "bold") + T(x + sw - 10, y + 24, 11, ":" + p, DIM, anchor="end")
        for j, line in enumerate(_wrap(d, 21)[:2]):
            b += T(x + 14, y + 47 + j * 16, 11.5, line, TEXT)
    b += T(32, 436, 13, "// PYTHON AI SERVICES (FastAPI)", DIM)
    ai = [("PRICE PREDICTOR", "XGBoost trip-cost prediction API"), ("FLEET OPTIMIZER", "greedy + genetic + local search"),
          ("IBOA", "alert scoring & delivery via RabbitMQ"), ("AYSHAA RAG", "LLM + RAG + tool calling agent")]
    for i, (n, d) in enumerate(ai):
        x, y = 32 + i * (sw + 12), 448
        b += panel(x, y, sw, 76, stroke=PURPLE + "99", fill="#0c0b1d")
        b += T(x + 14, y + 26, 13, n, "#ffffff", "bold")
        for j, line in enumerate(_wrap(d, 21)[:2]):
            b += T(x + 14, y + 47 + j * 16, 11.5, line, "#c9b6ff")
    b += T(32, 552, 13, "// CLIENTS", DIM)
    cl = [("BACK-OFFICE", "React · Vite · TS"), ("CLIENT PORTAL", "Next.js 14"), ("DRIVER APP", "Expo · RN")]
    cw = (W - 64 - 2 * 12) // 3
    for i, (n, d) in enumerate(cl):
        x = 32 + i * (cw + 12)
        b += panel(x, 562, cw, 30, stroke=CYAN + "66", fill="#08111f", rx=6)
        b += T(x + 12, 582, 12.5, n, CYAN, "bold") + T(x + cw - 12, 582, 11.5, d, TEXT, anchor="end")
    save("xpark-panel.svg", svg(W, h, b, "XPARK GMAO — control panel",
         "Overview of XPARK GMAO: 8 .NET 8 microservices, 4 Python AI services, 3 client applications, 20 docker-compose services."))


def arrow(x1, y1, x2, y2, c=CYAN, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{c}" stroke-width="1.8" fill="none"{d}/>'
            f'<path d="M{x2} {y2}l-5 -8h10z" fill="{c}" transform="rotate({90 if y2>y1 else -90} {x2} {y2}) rotate(0)" opacity="0"/>')


def vline(x, y1, y2, c=CYAN, dash="", head=True):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = f'<path d="M{x} {y1}V{y2}" stroke="{c}" stroke-width="1.8" fill="none"{d}/>'
    if head:
        s += f'<path d="M{x-5} {y2-8}L{x} {y2}L{x+5} {y2-8}z" fill="{c}"/>'
    return s


def xpark_arch():
    h = 560
    b = bg(W, h)
    b += T(32, 34, 14, "$ cat xpark/architecture.txt", GREEN, "bold") + T(W - 32, 34, 12, "derived from docker-compose.yml + nginx.conf", DIM, anchor="end")
    # clients
    cl = [("Back-office", "React 18 · Vite · TS · :3000"), ("Client portal", "Next.js 14 · :3001"), ("Driver app", "Expo · RN · GPS → Mission.API")]
    cw = 236
    for i, (n, d) in enumerate(cl):
        x = 32 + i * (cw + 12)
        b += panel(x, 52, cw, 56, stroke=CYAN + "88", fill="#08111f")
        b += T(x + 14, 78, 15, n, "#ffffff", "bold") + T(x + 14, 98, 12, d, TEXT)
        b += vline(x + cw / 2, 108, 134)
    # gateway
    b += panel(32, 134, W - 64, 44, stroke=BLUE, fill="#07142b")
    b += T(48, 161, 15, "NGINX gateway :8080", "#ffffff", "bold") + T(W - 48, 161, 12, "/iam /fleet /mission /maintenance /finance /alerts /prediction /chat", TEXT, anchor="end")
    b += vline(W / 2, 178, 204)
    # services
    b += panel(32, 204, W - 64, 118, stroke=BLUE, fill="#07142b")
    b += T(48, 226, 15, "8 × ASP.NET Core 8 microservices", "#ffffff", "bold")
    b += T(48, 244, 11.5, "EF Core (Npgsql) · JWT · MassTransit · Serilog · AutoMapper", DIM)
    names = ["IAM", "Fleet", "Mission", "Maintenance", "Finance", "Alerts", "Chat", "Prediction"]
    nw = (W - 96 - 7 * 8) // 8
    for i, n in enumerate(names):
        x = 48 + i * (nw + 8)
        b += panel(x, 254, nw, 28, stroke=CYAN + "66", fill="#08111f", rx=5)
        b += T(x + nw / 2, 273, 10.5 if len(n) > 8 else 11.5, n, TEXT, anchor="middle")
    b += T(48, 306, 11.5, "each service: API → Application → Domain ← Infrastructure", DIM)
    # infra
    b += vline(200, 322, 348) + vline(600, 322, 348)
    b += panel(32, 348, 368, 52, stroke=CYAN + "99", fill="#08111f")
    b += T(48, 372, 15, "PostgreSQL 16", "#ffffff", "bold") + T(48, 391, 12, "shared database across services", TEXT)
    b += panel(412, 348, 356, 52, stroke=CYAN + "99", fill="#08111f")
    b += T(428, 372, 15, "RabbitMQ 3.13", "#ffffff", "bold") + T(428, 391, 12, "event bus · exchange xpark.ai", TEXT)
    b += vline(600, 400, 426)
    # AI
    b += panel(32, 426, W - 64, 112, stroke=PURPLE, fill="#0c0b1d")
    b += T(48, 449, 15, "Python AI services · FastAPI", "#ffffff", "bold")
    b += T(48, 465, 11.5, "ports: ai-predictor 8000 · ai-optimizer 8001 · iboa 5008 · ayshaa-rag 8010", "#c9b6ff")
    ai = [("Price predictor", "XGBoost"), ("Fleet optimizer", "GA + search"), ("IBOA", "alert scoring"), ("AyshaaRAG", "Qdrant · Ollama")]
    aw = (W - 96 - 3 * 10) // 4
    for i, (n, d) in enumerate(ai):
        x = 48 + i * (aw + 10)
        b += panel(x, 474, aw, 52, stroke=PURPLE + "99", fill="#0f0d24", rx=6)
        b += T(x + 12, 496, 13.5, n, "#ffffff", "bold") + T(x + 12, 515, 12, d, "#c9b6ff")
    save("xpark-architecture.svg", svg(W, h, b, "XPARK GMAO — architecture",
         "Architecture: three client apps, an Nginx gateway, eight .NET 8 microservices, PostgreSQL and RabbitMQ, and four Python AI services."))


# ───────────────────────────── CryptoVisionAI ─────────────────────────────
def crypto_panel():
    h = 446
    b = bg(W, h)
    b += brackets(10, 10, W - 20, h - 20, PURPLE, 18, 3)
    b += T(32, 44, 14, "FEATURED PROJECT // AI / ML", PURPLE, "bold")
    b += T(32, 80, 32, "CryptoVisionAI", "#ffffff", "bold", extra='filter="url(#glow)"')
    b += T(32, 106, 15, "candlestick charts → CNN → BUY / SELL / HOLD classification", CYAN)
    stages = [("01 DATA", "Binance 1-min OHLCV", "Kaggle dataset · parquet"), ("02 IMAGE", "30-candle windows", "224×224 chart images"),
              ("03 LABEL", "5-bar forward return", "±0.15% threshold"), ("04 MODEL", "CNN (custom / ResNet50)", "TensorFlow + PyTorch"),
              ("05 OUTPUT", "3-class signal", "BUY · SELL · HOLD")]
    sw, gap = 136, 15
    for i, (t, a, c) in enumerate(stages):
        x = 32 + i * (sw + gap)
        b += panel(x, 128, sw, 110, stroke=(PURPLE if i in (3, 4) else CYAN) + "99", fill="#08111f")
        b += T(x + 12, 152, 13, t, PURPLE if i in (3, 4) else CYAN, "bold")
        # wrap helper
        for j, line in enumerate(_wrap(a, 15)):
            b += T(x + 12, 178 + j * 17, 13, line, "#ffffff", "bold")
        for j, line in enumerate(_wrap(c, 16)):
            b += T(x + 12, 214 + j * 15, 11.5, line, DIM)
        if i < 4:
            b += f'<path d="M{x+sw+2} 183h{gap-6}" stroke="{CYAN}" stroke-width="2"/><path d="M{x+sw+gap-6} 178l6 5l-6 5z" fill="{CYAN}"/>'
    # label balance bar (documented)
    b += T(32, 270, 13, "// LABEL BALANCE (as documented in the repo: 254,424 images · 70/15/15 split)", DIM)
    bx, bw = 32, W - 64
    parts = [("BUY 26.5%", 26.5, GREEN), ("SELL 26.9%", 26.9, PURPLE), ("HOLD 46.6%", 46.6, BLUE)]
    x = bx
    for lab, pct, col in parts:
        w = bw * pct / 100
        b += f'<rect x="{x:.1f}" y="282" width="{w-3:.1f}" height="26" rx="4" fill="{col}" opacity=".85"/>'
        b += T(x + (w - 3) / 2, 300, 13, lab, "#04070d", "bold", "middle")
        x += w
    # status board
    b += T(32, 340, 13, "// STATUS — what the repository actually contains", DIM)
    b += panel(32, 352, 372, 74, stroke=GREEN + "99", fill="#07160f")
    b += T(46, 374, 13, "● IMPLEMENTED", GREEN, "bold")
    for j, line in enumerate(_wrap("dataset pipeline · model definitions · training scripts (TensorFlow + PyTorch)", 44)):
        b += T(46, 394 + j * 16, 11.5, line, TEXT)
    b += panel(416, 352, 352, 74, stroke=PURPLE + "99", fill="#110c22")
    b += T(430, 374, 13, "○ NOT PUBLISHED", PURPLE, "bold")
    for j, line in enumerate(_wrap("trained weights · accuracy figures · backtest results", 40)):
        b += T(430, 394 + j * 16, 11.5, line, TEXT)
    save("cryptovision-panel.svg", svg(W, h, b, "CryptoVisionAI — pipeline",
         "Pipeline: Binance data, 30-candle chart images, 5-bar forward-return labels, CNN model, BUY/SELL/HOLD output. Trained weights and metrics are not published."))


def _wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def main():
    os.makedirs(OUT, exist_ok=True)
    header()
    hero()
    divider()
    footer()
    tech()
    xpark_panel()
    xpark_arch()
    crypto_panel()
    banner("cmd-about.svg", "01", "cat about-me.txt", "[01] about")
    banner("cmd-stack.svg", "02", "./tech-stack.sh", "[02] technical universe")
    banner("cmd-flagship.svg", "03", "./launch xpark-gmao", "[03] flagship project")
    banner("cmd-featured.svg", "04", "./launch cryptovisionai", "[04] featured project")
    banner("cmd-projects.svg", "05", "ls ./projects", "[05] project directory")
    banner("cmd-status.svg", "06", "./system-status.sh", "[06] diagnostics")
    banner("cmd-contact.svg", "07", "./connect.sh", "[07] contact")


if __name__ == "__main__":
    main()
