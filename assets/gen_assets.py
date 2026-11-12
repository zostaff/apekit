#!/usr/bin/env python3
"""Regenerates every SVG in assets/:  python3 assets/gen_assets.py"""
import os, math, random
from xml.sax.saxutils import escape

HERE = os.environ.get("APEKIT_OUT") or os.path.dirname(os.path.abspath(__file__))
W = 1260
FONT = "Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono','Courier New',monospace"
CW = 7.83  # char advance at 13px Menlo

# palette: neon terminal
BG0, BG1, BG2 = "#0b2a12", "#050a06", "#020402"
NEON, NEON2, LIME = "#00ff41", "#39ff88", "#b6ff3b"
CYN, RED, MAG, ORG = "#3de8ff", "#ff4d6d", "#ff4fd8", "#ffb347"
TXT, MUT, DIM = "#d9ffe3", "#5fa173", "#2f5a3a"
BORDER, PANEL = "#16502a", "#06100a"
TITLE_STOPS = ["#f0fff3", "#8dffae", NEON, "#00c853"]
EXTRUDE = ["#03200c", "#052c11", "#073a17", "#0a4a1d", "#0e5e25"]
BUY, DEEP, PALE = NEON, "#00a82b", "#c8ffd6"

THEMES = {
  "matrix": {},
  "synth": dict(BG0="#2b0a2e", BG1="#0a040c", BG2="#040205", NEON="#ff2bd6", NEON2="#ff7ae6", LIME="#c77dff",
                CYN="#3de8ff", RED="#ff4d6d", MAG="#ffb3f0", ORG="#ff9e5e", TXT="#ffe6fa", MUT="#a46a9c", DIM="#5a3354",
                BORDER="#4f1a4a", PANEL="#10060f", TITLE_STOPS=["#fff0fb", "#ff9be9", "#ff2bd6", "#9d4edd"],
                EXTRUDE=["#1c0420", "#2a0630", "#3a0942", "#4c0c55", "#600f6b"], BUY="#3de8ff", DEEP="#a3008a", PALE="#ffd6f6"),
  "ice": dict(BG0="#06263a", BG1="#03090f", BG2="#010407", NEON="#00e5ff", NEON2="#7df9ff", LIME="#6b8cff",
              CYN="#b18cff", RED="#ff4d6d", MAG="#ff6ad5", ORG="#ffb347", TXT="#e0fbff", MUT="#5f93a8", DIM="#2c4c5c",
              BORDER="#134257", PANEL="#040d14", TITLE_STOPS=["#f2feff", "#9df3ff", "#00d0ff", "#2f6bff"],
              EXTRUDE=["#021a2c", "#03243b", "#05304e", "#073e63", "#0a4e7b"], BUY="#39ff88", DEEP="#0083c9", PALE="#d2f9ff"),
  "blood": dict(BG0="#2e0508", BG1="#0b0304", BG2="#050102", NEON="#ff2a4d", NEON2="#ff7a8c", LIME="#ff6a3d",
                CYN="#3de8ff", RED="#ff9e3d", MAG="#ff4fd8", ORG="#ffb347", TXT="#ffe6e9", MUT="#a8656e", DIM="#5c2c33",
                BORDER="#571520", PANEL="#120406", TITLE_STOPS=["#fff0f2", "#ff98a6", "#ff2a4d", "#b0001e"],
                EXTRUDE=["#200306", "#2e040a", "#3f060e", "#520812", "#680b17"], BUY="#39ff88", DEEP="#a8001c", PALE="#ffd3da"),
  "void": dict(BG0="#170a33", BG1="#06040d", BG2="#030207", NEON="#8b5cff", NEON2="#b69bff", LIME="#3de8ff",
               CYN="#ff6ad5", RED="#ff4d6d", MAG="#ff9de2", ORG="#ffb347", TXT="#ece6ff", MUT="#7d6fa8", DIM="#3c3460",
               BORDER="#2a1d5c", PANEL="#090614", TITLE_STOPS=["#f4f0ff", "#c3b0ff", "#8b5cff", "#4c1dd6"],
               EXTRUDE=["#0e0624", "#150a33", "#1d0e46", "#26135b", "#311872"], BUY="#39ff88", DEEP="#5a2fd6", PALE="#e2d8ff"),
}
globals().update(THEMES.get(os.environ.get("APEKIT_THEME", "blood"), {}))

PIX = {
 'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
 'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
 'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
 'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
 'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
 'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
 'G': [".####", "#....", "#....", "#..##", "#...#", "#...#", ".####"],
 'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
 'I': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
 'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
 'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
 'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
 'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
 'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
 'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
 'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
 'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
 'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
 'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
 'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
 'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
 'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
 'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
 'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
 'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
 'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
 '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
 '1': ["..#..", ".##..", "#.#..", "..#..", "..#..", "..#..", "#####"],
 '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
 '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
 '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
 '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
 '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
 ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
 '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
}


def lerp(c1, c2, t):
    c1 = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    c2 = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(c1, c2))


def grad(stops, t):
    t = max(0.0, min(1.0, t))
    n = len(stops) - 1
    i = min(int(t * n), n - 1)
    return lerp(stops[i], stops[i + 1], t * n - i)


class SVG:
    def __init__(self, h, title):
        self.h, self.out = h, []
        self.a(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<title>{escape(title)}</title>
<defs>
<radialGradient id="bg" cx="0.5" cy="0" r="1.2"><stop offset="0" stop-color="{BG0}"/><stop offset="0.6" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></radialGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{NEON}" stop-opacity="0.16"/><stop offset="1" stop-color="{NEON}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="1.3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bigglow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="dots" width="8" height="8" patternUnits="userSpaceOnUse"><rect x="3" y="3" width="1.6" height="1.6" fill="{NEON}" fill-opacity="0.07"/></pattern>
<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity="0.3"/></pattern>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{NEON}"/></marker>
<marker id="arrc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{CYN}"/></marker>
<marker id="arrm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MAG}"/></marker>
<marker id="arrd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MUT}"/></marker>
<clipPath id="frame"><rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="14"/></clipPath>
</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="14" fill="url(#bg)"/>
<g clip-path="url(#frame)">
<rect width="{W}" height="{h}" fill="url(#dots)"/>
<g font-family="{FONT}" xml:space="preserve">''')

    def a(self, s):
        self.out.append(s)

    def runs(self, x, y, parts, size=13, anchor_end=False):
        cw = CW * size / 13
        total = sum(len(s) for s, _ in parts) * cw
        cx = x - total if anchor_end else x
        spans = []
        for s, c in parts:
            lead = len(s) - len(s.lstrip(" "))
            if s.strip():
                spans.append(f'<tspan x="{cx + lead*cw:.1f}" fill="{c}">{escape(s.lstrip(" "))}</tspan>')
            cx += len(s) * cw
        self.a(f'<text y="{y:.1f}" font-size="{size}" font-weight="700">{"".join(spans)}</text>')

    def text_c(self, cx, y, s, fill, size=13):
        self.runs(cx - len(s) * CW * size / 13 / 2, y, [(s, fill)], size)

    def box(self, x, y, w, h, accent, fill=PANEL, op=0.6, rx=8, dash=None, sw=1.4):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" fill-opacity="0.85" stroke="{accent}" stroke-opacity="{op}" stroke-width="{sw}"{d}/>')

    def corners(self, x, y, w, h, accent, L=10):
        p = []
        for (cx, cy, dx, dy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            p.append(f"M{cx + dx*L:.1f} {cy:.1f} L{cx:.1f} {cy:.1f} L{cx:.1f} {cy + dy*L:.1f}")
        self.a(f'<path d="{" ".join(p)}" fill="none" stroke="{accent}" stroke-width="2.2"/>')

    def panel(self, x, y, w, h, title_parts, accent):
        self.box(x, y, w, h, accent, op=0.55, rx=10)
        tw = sum(len(s) for s, _ in title_parts) * CW + 16
        self.a(f'<rect x="{x+16}" y="{y-9}" width="{tw:.1f}" height="18" fill="{BG1}"/>')
        self.runs(x + 24, y + 4.5, title_parts)

    def sep(self, x1, x2, y):
        self.a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{BORDER}" stroke-dasharray="3 3"/>')

    def line(self, d, color=NEON, marker="arr", dash=None, op=0.85, sw=1.5):
        m = f' marker-end="url(#{marker})"' if marker else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.a(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{sw}"{ds}{m}/>')

    def pixel_word(self, word, x, y, px, stops=TITLE_STOPS, extrude=EXTRUDE, glow=True, gap=1):
        cells = []
        col = 0
        for ch in word:
            g = PIX[ch]
            for r, row in enumerate(g):
                for c, p in enumerate(row):
                    if p == "#":
                        cells.append((col + c, r))
            col += 5 + gap
        cols = col - gap
        step = max(px * 0.1, 1.1)
        for k in range(len(extrude), 0, -1):
            off = k * step
            self.a(f'<g fill="{extrude[len(extrude)-k]}">' + "".join(
                f'<rect x="{x + cx*px + off:.1f}" y="{y + cy*px + off:.1f}" width="{px}" height="{px}"/>' for cx, cy in cells) + '</g>')
        face = []
        for cx, cy in cells:
            c = grad(stops, (cx + cy * 0.4) / (cols + 2.8))
            face.append(f'<rect x="{x + cx*px:.1f}" y="{y + cy*px:.1f}" width="{px}" height="{px}" fill="{c}"/>')
            face.append(f'<rect x="{x + cx*px:.1f}" y="{y + cy*px:.1f}" width="{px}" height="{px*0.14:.1f}" fill="#fff" fill-opacity="0.2"/>')
        self.a((f'<g filter="url(#bigglow)">' if glow else '<g>') + "".join(face) + '</g>')
        gl = []
        for cx, cy in cells:
            X, Y = x + cx * px, y + cy * px
            gl.append(f'<rect x="{X+px-px*0.07:.1f}" y="{Y:.1f}" width="{px*0.07:.1f}" height="{px}"/><rect x="{X:.1f}" y="{Y+px-px*0.08:.1f}" width="{px}" height="{px*0.08:.1f}"/>')
        self.a(f'<g fill="{BG1}" fill-opacity="0.6">' + "".join(gl) + '</g>')
        return cols * px

    def cube(self, cx, cy, s, glow=True):
        """isometric pixel cube = the bundle"""
        dx, dy = s * 0.866, s * 0.5
        top = f"M{cx} {cy-s} L{cx+dx} {cy-s+dy} L{cx} {cy} L{cx-dx} {cy-s+dy} Z"
        left = f"M{cx-dx} {cy-s+dy} L{cx} {cy} L{cx} {cy+s} L{cx-dx} {cy+dy} Z"
        right = f"M{cx+dx} {cy-s+dy} L{cx} {cy} L{cx} {cy+s} L{cx+dx} {cy+dy} Z"
        g = ' filter="url(#bigglow)"' if glow else ""
        self.a(f'<g{g}><path d="{top}" fill="{PALE}"/><path d="{left}" fill="{NEON}"/><path d="{right}" fill="{DEEP}"/></g>')
        # tape across the top + sides
        t = s * 0.16
        self.a(f'<path d="M{cx-dx/2-t*0.9} {cy-s+dy/2+ t*0.5} L{cx+dx/2-t*0.9} {cy-dy/2 + t*0.5 + dy*0} L{cx+dx/2+t*0.9} {cy-dy/2-t*0.5} L{cx-dx/2+t*0.9} {cy-s+dy/2-t*0.5} Z" fill="{BG1}" fill-opacity="0.55"/>')
        # pixel grid overlay on faces
        lines = []
        n = 6
        for i in range(1, n):
            f = i / n
            lines.append(f"M{cx-dx + dx*f:.1f} {cy-s+dy + dy*f:.1f} L{cx-dx + dx*f:.1f} {cy+dy + dy*f:.1f}")
            lines.append(f"M{cx-dx:.1f} {cy-s+dy + s*f:.1f} L{cx:.1f} {cy + s*f:.1f}")
            lines.append(f"M{cx + dx*f:.1f} {cy + dy*0 - dy*f + dy*f*0:.1f} L{cx + dx*f:.1f} {cy+s - dy*f:.1f}")
            lines.append(f"M{cx:.1f} {cy + s*f:.1f} L{cx+dx:.1f} {cy-s+dy + s*f:.1f}")
        self.a(f'<path d="{" ".join(lines)}" stroke="{BG1}" stroke-opacity="0.35" stroke-width="1.4" fill="none"/>')
        self.a(f'<path d="{top} {left} {right}" fill="none" stroke="#eafff0" stroke-opacity="0.5" stroke-width="1"/>')

    def save(self, name):
        self.a(f'</g></g><rect x="0.5" y="0.5" width="{W-1}" height="{self.h-1}" rx="14" fill="url(#scan)" stroke="{BORDER}"/></svg>')
        with open(os.path.join(HERE, name), "w") as f:
            f.write("\n".join(self.out))
        print("wrote", name)


def topbar(s, left, right_parts):
    s.a('<g filter="url(#glow)">')
    for i, c in enumerate([RED, ORG, NEON]):
        s.a(f'<circle cx="{38+i*16}" cy="36" r="4.6" fill="{c}"/>')
    s.runs(102, 40.5, [(left, MUT)])
    s.runs(W - 38, 40.5, right_parts, anchor_end=True)
    s.a('</g>')


# ===================================================================== hero
def hero():
    H = 700
    s = SVG(H, "APEKIT: pump.fun bundler and volume bot")
    s.a(f'<ellipse cx="520" cy="130" rx="560" ry="160" fill="url(#halo)"/>')
    topbar(s, "~/apekit · pump.fun bundler + volume bot · solana mainnet",
           [("v1.0.0 · node 22 · ", MUT), ("● ", NEON), ("armed", NEON)])
    s.pixel_word("APEKIT", 66, 68, 22)

    # bundle cube + orbiting wallets
    cx, cy = 1050, 150
    s.a(f'<ellipse cx="{cx}" cy="{cy+8}" rx="150" ry="52" fill="none" stroke="{NEON}" stroke-opacity="0.35" stroke-dasharray="3 5"/>')
    for i, (ang, lab) in enumerate([(200, "w01"), (340, "w02"), (20, "w03"), (160, "w04")]):
        r = math.radians(ang)
        wx, wy = cx + 150 * math.cos(r), cy + 8 + 52 * math.sin(r)
        s.a(f'<line x1="{wx:.1f}" y1="{wy:.1f}" x2="{cx}" y2="{cy}" stroke="{NEON}" stroke-opacity="0.25" stroke-dasharray="2 4"/>')
    s.cube(cx, cy + 10, 62)
    for i, (ang, lab) in enumerate([(200, "w01"), (340, "w02"), (20, "w03"), (160, "w04")]):
        r = math.radians(ang)
        wx, wy = cx + 150 * math.cos(r), cy + 8 + 52 * math.sin(r)
        s.a(f'<g filter="url(#glow)"><rect x="{wx-19:.1f}" y="{wy-10:.1f}" width="38" height="20" rx="4" fill="{BG1}" stroke="{NEON}" stroke-opacity="0.8"/></g>')
        s.text_c(wx, wy + 4.5, lab, NEON, 12)
    s.runs(cx - 52, cy + 108, [("[ ", DIM), ("1 SLOT", NEON), (" ]", DIM)])

    s.a('<g filter="url(#glow)">')
    s.runs(70, 254, [("> ", NEON), ("funds the wallets", TXT), (" . ", DIM), ("bundles the buys", TXT), (" . ", DIM),
                     ("churns the volume", TXT), (" . ", DIM), ("drains it home", TXT), ("_", NEON)], size=15)
    s.runs(70, 280, [("[ ", DIM), ("FUND", NEON), (" ]──[ ", DIM), ("BUNDLE", CYN), (" ]──[ ", DIM), ("VOLUME", LIME),
                     (" ]──[ ", DIM), ("SELL", RED), (" ]──[ ", DIM), ("DRAIN", MAG), (" ]", DIM)])
    s.a('</g>')

    PY, PH = 312, 330
    s.a('<g filter="url(#glow)">')
    # FUND
    x0, w0 = 30, 372
    s.panel(x0, PY, w0, PH, [("● ", NEON), ("FUND ", NEON), (" data/wallets.json", TXT)], NEON)
    s.runs(x0 + 20, PY + 34, [("master ", MUT), ("7xKX…AsU", TXT), ("   ", MUT), ("4.2000 SOL", NEON)])
    s.runs(x0 + 20, PY + 54, [("  └─ split 0.34 SOL → 4 fresh keypairs", DIM)])
    ws = [("w01", "9pMH…Bgm", "0.0830"), ("w02", "DYdf…Qe1", "0.0850"), ("w03", "3sVr…T1c", "0.0810"),
          ("w04", "HfQ2…9Lm", "0.0840")]
    for i, (n, ad, sol) in enumerate(ws):
        y = PY + 84 + i * 30
        s.runs(x0 + 20, y, [(n + "  ", MUT), (ad + "  ", TXT), (sol + " SOL ", NEON2), ("ok", NEON)])
        bw = 56 * float(sol) / 0.085
        s.a(f'<rect x="{x0 + w0 - 80}" y="{y-9}" width="{bw:.1f}" height="9" fill="{NEON}" fill-opacity="0.8"/>')
        s.a(f'<rect x="{x0 + w0 - 80 + bw:.1f}" y="{y-9}" width="{56-bw:.1f}" height="9" fill="{DIM}" fill-opacity="0.5"/>')
    s.sep(x0 + 16, x0 + w0 - 16, PY + 218)
    s.runs(x0 + 20, PY + 242, [("mode   ", MUT), ("jito", CYN), (" | staggered 2-5s", DIM)])
    s.runs(x0 + 20, PY + 262, [("tip    ", MUT), ("0.001", NEON), (" +0.001 SOL / retry", DIM)])
    s.runs(x0 + 20, PY + 296, [("$ ", NEON), ("npm run bundle -- <MINT> 4 0.34", TXT)])
    s.a(f'<rect x="{x0 + 20 + 34*CW:.1f}" y="{PY+285}" width="8" height="14" fill="{NEON}"/>')

    # BUNDLE
    x1, w1 = 422, 416
    s.panel(x1, PY, w1, PH, [("● ", CYN), ("BUNDLE ", CYN), (" jito · atomic", TXT)], CYN)
    s.runs(x1 + 20, PY + 34, [("slot ", MUT), ("467686675", TXT), ("   all land or none do", DIM)])
    bx, by, bw_, bh = x1 + 24, PY + 54, 220, 24
    txs = [("buy  w01", BUY, "0.0830"), ("buy  w02", BUY, "0.0850"), ("buy  w03", BUY, "0.0810"),
           ("buy  w04", BUY, "0.0840"), ("+ tip → jito", CYN, "0.001")]
    s.a(f'<rect x="{bx-8}" y="{by-8}" width="{bw_+16}" height="{len(txs)*(bh+5)+11}" rx="6" fill="none" stroke="{CYN}" stroke-opacity="0.7" stroke-dasharray="4 3"/>')
    for i, (lab, c, v) in enumerate(txs):
        y = by + i * (bh + 5)
        s.a(f'<rect x="{bx}" y="{y}" width="{bw_}" height="{bh}" rx="3" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-opacity="0.8"/>')
        s.a(f'<rect x="{bx}" y="{y}" width="5" height="{bh}" fill="{c}"/>')
        s.runs(bx + 14, y + 16.5, [(f"tx{i}  ", MUT), (lab, TXT)])
        s.runs(bx + bw_ - 8, y + 16.5, [(v, c)], anchor_end=True)
    ex = bx + bw_ + 26
    my = by + 2.5 * (bh + 5) - 2
    for i, e in enumerate(["mainnet", "amsterdam", "tokyo"]):
        ey = by + 26 + i * 48
        s.line(f"M{bx+bw_+8} {my} C{ex-6} {my} {ex-12} {ey-5} {ex+2} {ey-5}", CYN, None, op=0.6, sw=1.3)
        s.a(f'<rect x="{ex+2}" y="{ey-17}" width="{len(e)*CW+18:.1f}" height="24" rx="4" fill="{BG1}" stroke="{CYN}" stroke-opacity="0.6"/>')
        s.runs(ex + 11, ey, [(e, CYN)])
    s.sep(x1 + 16, x1 + w1 - 16, PY + 218)
    cx0, cy0, cw0, ch0 = x1 + 24, PY + 232, w1 - 48, 64
    pts = []
    for i in range(60):
        t = i / 59
        b = 0.08 + 0.05 * t + (0.55 + 0.25 * (t - 0.32) if t > 0.32 else 0) + 0.02 * math.sin(i * 1.7)
        pts.append((cx0 + t * cw0, cy0 + ch0 - b * ch0))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    s.a(f'<path d="{d} L{cx0+cw0} {cy0+ch0} L{cx0} {cy0+ch0} Z" fill="{BUY}" fill-opacity="0.1"/>')
    s.a(f'<path d="{d}" fill="none" stroke="{BUY}" stroke-width="2"/>')
    jx = cx0 + 0.32 * cw0
    s.a(f'<line x1="{jx:.1f}" y1="{cy0-2}" x2="{jx:.1f}" y2="{cy0+ch0}" stroke="{CYN}" stroke-dasharray="2 3"/>')
    s.runs(jx + 8, cy0 + 10, [("bundle landed", CYN)])
    s.runs(cx0, cy0 + ch0 + 20, [("bonding curve", MUT), ("  x·y=k", DIM)])

    # VOLUME
    x2, w2 = 858, 372
    s.panel(x2, PY, w2, PH, [("● ", LIME), ("VOLUME ", LIME), (" churn loop", TXT)], LIME)
    s.runs(x2 + 20, PY + 34, [("wallets ", MUT), ("12", TXT), ("  bias ", MUT), ("65%", BUY), ("  run ", MUT), ("15m", TXT)])
    log = [("[buy] ", BUY, "Bz8ekPw1... 0.0310 SOL"), ("[buy] ", BUY, "HfQ29Lm4... 0.0180 SOL"),
           ("[sell]", RED, "3sVrT1c9... 42%"), ("[buy] ", BUY, "9pMHBgm2... 0.0420 SOL"),
           ("[buy] ", BUY, "Ge87pR2x... 0.0150 SOL"), ("[sell]", RED, "DYdfQe17... 63%"),
           (None, DIM, "pause · lru rotate")]
    for i, (tag, c, rest) in enumerate(log):
        y = PY + 60 + i * 21
        if tag is None:
            s.runs(x2 + 20, y, [("······ ", DIM), (rest, DIM)])
        else:
            s.runs(x2 + 20, y, [(tag + " ", c), (rest, TXT)])
    s.sep(x2 + 16, x2 + w2 - 16, PY + 218)
    vx, vy, vh = x2 + 22, PY + 232, 58
    random.seed(7)
    n = 30
    bwid = (w2 - 44) / n
    for i in range(n):
        b = 0.25 + 0.75 * random.random()
        sv = b * (0.35 if random.random() < 0.65 else 0.7)
        hb, hs = b * vh * 0.62, sv * vh * 0.62
        xx = vx + i * bwid
        s.a(f'<rect x="{xx:.1f}" y="{vy + vh - hb:.1f}" width="{bwid-2:.1f}" height="{hb:.1f}" fill="{BUY}" fill-opacity="0.85"/>')
        s.a(f'<rect x="{xx:.1f}" y="{vy + vh - hb - hs - 1:.1f}" width="{bwid-2:.1f}" height="{hs:.1f}" fill="{RED}" fill-opacity="0.8"/>')
    s.runs(x2 + 20, vy + vh + 26, [("buys ", MUT), ("65%", BUY), ("   sells ", MUT), ("35%", RED), ("   jittered fees", DIM)])
    s.a('</g>')
    foot = "illustration · panel numbers are an example"
    s.runs(W / 2 - len(foot) * CW / 2, H - 24, [(foot, DIM)])
    s.save("hero.svg")


# ===================================================================== divider
def divider():
    H = 32
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{NEON}" stop-opacity="0"/>'
           f'<stop offset="0.5" stop-color="{NEON}" stop-opacity="0.9"/><stop offset="1" stop-color="{NEON}" stop-opacity="0"/></linearGradient>'
           f'<filter id="glow"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{BG1}" stroke="{BORDER}"/>',
           f'<g filter="url(#glow)"><rect x="40" y="15.4" width="{W/2-70}" height="1.2" fill="url(#g)"/>',
           f'<rect x="{W/2+30}" y="15.4" width="{W/2-70}" height="1.2" fill="url(#g)"/>']
    for x in (140, 330, W - 330, W - 140):
        out.append(f'<rect x="{x-3}" y="13" width="6" height="6" transform="rotate(45 {x} 16)" fill="{NEON}" fill-opacity="0.7"/>')
    out.append(f'<rect x="{W/2-28}" y="9" width="2" height="14" fill="{NEON}"/><rect x="{W/2+26}" y="9" width="2" height="14" fill="{NEON}"/>')
    for i in range(4):
        out.append(f'<rect x="{W/2-16 + i*8}" y="{11 + (i%2)*5}" width="6" height="6" fill="{NEON if i != 2 else CYN}"/>')
    out.append('</g></svg>')
    with open(os.path.join(HERE, "divider.svg"), "w") as f:
        f.write("\n".join(out))
    print("wrote divider.svg")


# ===================================================================== section headers
SECTIONS = [
    ("01", "BOOT", "three commands from clone to armed", "#boot"),
    ("02", "BUNDLER", "n wallets . one slot . all land or none do", "#bundler"),
    ("03", "VOLUME", "lru rotation . 65/35 bias . jittered timing", "#volume"),
    ("04", "EXIT", "sell every bag . drain every lamport home", "#exit"),
    ("05", "INTERNALS", "four scripts . six modules . five deps", "#internals"),
    ("06", "RULES", "read this before you ape anything", "#rules"),
]


def section(num, title, sub, tag):
    H = 150
    s = SVG(H, f"{num} {title}")
    s.a(f'<ellipse cx="420" cy="70" rx="420" ry="90" fill="url(#halo)"/>')
    s.pixel_word(num, 40, 30, 12.5, stops=[TITLE_STOPS[0], NEON, DEEP])
    s.pixel_word(title, 205, 30, 7.2, gap=1)
    s.a('<g filter="url(#glow)">')
    s.runs(207, 106, [("// ", DIM), (sub, MUT)])
    s.runs(207, 128, [("─┤ ", NEON), (tag, NEON2), (" ├", NEON)])
    s.a(f'<line x1="{207 + (len(tag)+5)*CW:.1f}" y1="124" x2="{W-210}" y2="124" stroke="{NEON}" stroke-opacity="0.5"/>')
    s.a('</g>')
    s.cube(W - 110, 72, 34)
    s.save(f"section-{num}.svg")


# ===================================================================== bundler flow
def flow():
    H = 470
    s = SVG(H, "apekit bundler pipeline: master, fund wallets, jito bundle, sell, drain")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("bundler pipeline", NEON), ("   master → fund → bundle → sell → drain", MUT)])
    s.runs(W - 40, 40, [("bundle.mjs · sell.mjs · drain.mjs", DIM)], anchor_end=True)

    stages = [
        ("01", "MASTER", NEON, ["MASTER_KEY in .env", "pays for the run", "needs budget × 1.3", "aborts if short"]),
        ("02", "FUND WALLETS", NEON2, ["generateWallets(N)", "fresh keypairs", "≤10 transfers / tx", "settle 2s"]),
        ("03", "JITO BUNDLE", CYN, ["buildBuyTx × N", "pump-sdk · 600k CU", "≤4 buys + tip tx", "5 attempts, tip ↑"]),
        ("04", "SELL", RED, ["data/wallets.json", "sell full balance", "top-up gas if dry", "per-wallet send"]),
        ("05", "DRAIN", MAG, ["drainWallets()", "sweep SOL → master", "5 in parallel", "keeps fee reserve"]),
    ]
    n = len(stages)
    bw, bh, gap = 206, 92, 37
    x0, y0 = 40, 78
    centers = []
    for i, (num, name, c, lines) in enumerate(stages):
        x = x0 + i * (bw + gap)
        centers.append(x + bw / 2)
        s.box(x, y0, bw, bh, c, op=0.8)
        s.corners(x, y0, bw, bh, c)
        s.runs(x + 16, y0 + 28, [(num + " ", DIM), (name, c)], size=15)
        s.runs(x + 16, y0 + 52, [(lines[0], TXT)])
        s.runs(x + 16, y0 + 72, [(lines[1], MUT)])
        if i < n - 1:
            s.line(f"M{x+bw+4} {y0+bh/2} L{x+bw+gap-4} {y0+bh/2}", c)
        # detail block
        dy = y0 + bh + 18
        s.box(x, dy, bw, 56, c, op=0.25, rx=6, dash="3 3")
        s.runs(x + 14, dy + 22, [("› ", c), (lines[2], MUT)])
        s.runs(x + 14, dy + 42, [("› ", c), (lines[3], MUT)])

    # jito fan-out under stage 03
    jx = centers[2]
    fy = y0 + bh + 18 + 56 + 26
    s.line(f"M{jx} {y0+bh+18+56+2} L{jx} {fy+8}", CYN, None, op=0.7)
    eps = ["mainnet", "amsterdam", "tokyo"]
    ex = [jx - 200, jx, jx + 200]
    s.line(f"M{ex[0]} {fy+8} L{ex[2]} {fy+8}", CYN, None, op=0.7)
    for x, e in zip(ex, eps):
        s.line(f"M{x} {fy+8} L{x} {fy+30}", CYN, "arrc", op=0.7)
        wdt = len(e) * CW + 22
        s.box(x - wdt / 2, fy + 32, wdt, 28, CYN, op=0.7, rx=5)
        s.text_c(x, fy + 51, e, CYN)
    s.text_c(jx, fy + 84, "block engines hit in parallel", DIM)

    # poll + fallback
    py_ = fy + 104
    s.box(jx - 290, py_, 270, 64, CYN, op=0.6)
    s.runs(jx - 276, py_ + 24, [("poll ", CYN), ("getInflightBundleStatuses", TXT)])
    s.runs(jx - 276, py_ + 46, [("  └ ", DIM), ("getBundleStatuses fallback", MUT)])
    s.box(jx + 20, py_, 270, 64, ORG, op=0.6, dash="4 3")
    s.runs(jx + 34, py_ + 24, [("fallback ", ORG), ("after 5 misses", TXT)])
    s.runs(jx + 34, py_ + 46, [("  └ ", DIM), ("individual sends", MUT)])
    s.line(f"M{jx-155} {fy+92} L{jx-155} {py_-4}", CYN, "arrc", op=0.5, dash="2 3")
    s.line(f"M{jx+155} {fy+92} L{jx+155} {py_-4}", ORG, None, op=0.5, dash="2 3")

    # left legend: atomic vs staggered
    lx, ly = 40, fy + 20
    s.runs(lx, ly, [("mode", MUT)])
    s.runs(lx, ly + 24, [("jito      ", CYN), ("atomic, 1 block", TXT)])
    s.runs(lx, ly + 46, [("staggered ", ORG), ("2-5s random gaps", TXT)])
    s.runs(lx, ly + 80, [("tip", MUT)])
    s.runs(lx, ly + 104, [("0.001", NEON), (" → ", DIM), ("0.005 SOL", NEON)])
    s.runs(lx, ly + 126, [("+0.001 per retry, cap 0.01", DIM)])

    # right legend
    rx = W - 40
    s.runs(rx, ly, [("state", MUT)], anchor_end=True)
    s.runs(rx, ly + 24, [("data/wallets.json", TXT)], anchor_end=True)
    s.runs(rx, ly + 46, [("keys + mint persisted", DIM)], anchor_end=True)
    s.runs(rx, ly + 80, [("fees", MUT)], anchor_end=True)
    s.runs(rx, ly + 104, [("p75 priority, cached 10s", TXT)], anchor_end=True)
    s.runs(rx, ly + 126, [("600k CU · token-2022 ok", DIM)], anchor_end=True)

    # return arc drain → master
    ry = y0 - 16
    s.line(f"M{centers[4]} {y0-2} L{centers[4]} {ry} L{centers[0]} {ry} L{centers[0]} {y0-4}", MAG, "arrm", op=0.6, dash="5 4")
    s.a(f'<rect x="{(centers[0]+centers[4])/2 - 120}" y="{ry-9}" width="240" height="18" fill="{BG1}"/>')
    s.text_c((centers[0] + centers[4]) / 2, ry + 4.5, "SOL flows back to master", MAG)
    s.a('</g>')
    s.save("flow.svg")


# ===================================================================== volume loop
def volume():
    H = 470
    s = SVG(H, "apekit volume bot: phases and churn loop")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("volume.mjs", LIME), ("   phases + churn loop", MUT)])
    s.runs(W - 40, 40, [("<MINT> 12 0.5 15 0.65", DIM)], anchor_end=True)

    # timeline (left)
    phases = [("1", "fund", "N wallets from master", NEON),
              ("2", "seed", "initial buys, 30-50% each", NEON2),
              ("3", "churn", "buy / sell for duration", LIME),
              ("4", "sell all", "dump remaining bags", RED),
              ("5", "drain", "SOL back to master", MAG)]
    tx, ty = 60, 90
    s.a(f'<line x1="{tx+12}" y1="{ty}" x2="{tx+12}" y2="{ty + 4*70}" stroke="{BORDER}" stroke-width="2"/>')
    for i, (n_, name, d, c) in enumerate(phases):
        y = ty + i * 70
        s.a(f'<rect x="{tx}" y="{y-12}" width="24" height="24" rx="4" fill="{BG1}" stroke="{c}" stroke-width="1.6"/>')
        s.text_c(tx + 12, y + 4.5, n_, c)
        s.runs(tx + 40, y - 1, [(name, c)], size=15)
        s.runs(tx + 40, y + 19, [(d, MUT)])
    s.a(f'<rect x="{tx-8}" y="{ty+2*70-24}" width="300" height="48" rx="6" fill="none" stroke="{LIME}" stroke-opacity="0.6" stroke-dasharray="3 3"/>')
    s.line(f"M{tx+296} {ty+140} C{560} {ty+140} {560} {255} {636} {255}", LIME)

    # ring (right)
    cx, cy, R = 800, 255, 150
    s.a(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{LIME}" stroke-opacity="0.35" stroke-dasharray="4 6"/>')
    nodes = [("pick wallet", "least-recently-used", LIME),
             ("roll bias", "65% BUY / 35% SELL", BUY),
             ("size trade", "random amount", NEON2),
             ("priority fee", "jitter on p75", CYN),
             ("sleep", "random gap", MUT),
             ("pause", "every 6-10 cycles", ORG)]
    pts = []
    for i in range(len(nodes)):
        ang = math.radians(-90 + i * 360 / len(nodes))
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    for i in range(len(nodes)):
        a1 = math.radians(-90 + i * 360 / len(nodes) + 14)
        a2 = math.radians(-90 + (i + 1) * 360 / len(nodes) - 14)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        x2, y2 = cx + R * math.cos(a2), cy + R * math.sin(a2)
        s.line(f"M{x1:.1f} {y1:.1f} A{R} {R} 0 0 1 {x2:.1f} {y2:.1f}", LIME, "arr", op=0.8, sw=1.8)
    for (x, y), (name, d, c) in zip(pts, nodes):
        w = max(len(name), len(d)) * CW + 26
        s.box(x - w / 2, y - 24, w, 48, c, op=0.85)
        s.text_c(x, y - 4, name, c)
        s.text_c(x, y + 15, d, MUT)
    s.text_c(cx, cy - 8, "churn", LIME, 18)
    s.text_c(cx, cy + 16, "until duration ends", DIM)

    # right column: trade split
    rx = 1030
    s.runs(rx, 110, [("per cycle", MUT)])
    s.a(f'<rect x="{rx}" y="124" width="{190*0.65:.1f}" height="16" fill="{BUY}" fill-opacity="0.85"/>')
    s.a(f'<rect x="{rx + 190*0.65 + 2:.1f}" y="124" width="{190*0.35-2:.1f}" height="16" fill="{RED}" fill-opacity="0.85"/>')
    s.runs(rx, 160, [("BUY ", BUY), ("65%", TXT), ("   SELL ", RED), ("35%", TXT)])
    s.runs(rx, 200, [("never same wallet", MUT)])
    s.runs(rx, 220, [("twice in a row", MUT)])
    s.runs(rx, 260, [("args", MUT)])
    for i, (k, v) in enumerate([("wallets", "12"), ("budget", "0.5 SOL"), ("duration", "15 min"), ("buy_bias", "0.65")]):
        s.runs(rx, 284 + i * 20, [(f"{k:<9}", DIM), (v, TXT)])
    s.a('</g>')
    s.save("volume.svg")


# ===================================================================== architecture
def arch():
    H = 470
    s = SVG(H, "apekit architecture: scripts, lib modules, externals")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("apekit/", NEON), ("   4 scripts → 6 modules → 5 deps", MUT)])

    scripts = [("bundle.mjs", "jito | staggered buys", CYN), ("volume.mjs", "buy/sell churn", LIME),
               ("sell.mjs", "sell every bag", RED), ("drain.mjs", "sweep SOL home", MAG)]
    mods = [("wallets.mjs", "keypairs"), ("utils.mjs", "retry, fees"), ("tx.mjs", "build + send"),
            ("jito.mjs", "bundle + poll"), ("fund.mjs", "fund + drain"), ("constants.mjs", "config")]
    ext = [("@pump-fun/pump-sdk", "curve maths + ix"), ("@solana/web3.js", "rpc + tx"),
           ("@solana/spl-token", "token ops"), ("jito block engine", "3 regions"), ("bs58 · bn.js", "encoding")]

    def row(items, y, bw, color_default, h=58):
        n = len(items)
        total = W - 80
        gap = (total - n * bw) / (n - 1)
        pos = {}
        for i, it in enumerate(items):
            name, d = it[0], it[1]
            c = it[2] if len(it) > 2 else color_default
            x = 40 + i * (bw + gap)
            s.box(x, y, bw, h, c, op=0.8)
            s.corners(x, y, bw, h, c, 8)
            s.runs(x + 14, y + 24, [(name, c)])
            s.runs(x + 14, y + 44, [(d, MUT)])
            pos[name] = (x + bw / 2, y, y + h)
        return pos

    P1 = row(scripts, 70, 250, NEON)
    P2 = row(mods, 220, 170, NEON2)
    P3 = row(ext, 370, 210, NEON2)
    s.runs(W - 40, 62, [("scripts", DIM)], anchor_end=True)
    s.runs(W - 40, 212, [("lib/", DIM)], anchor_end=True)
    s.runs(W - 40, 362, [("deps", DIM)], anchor_end=True)

    edges1 = {"bundle.mjs": ["wallets.mjs", "utils.mjs", "tx.mjs", "jito.mjs", "fund.mjs"],
              "volume.mjs": ["wallets.mjs", "utils.mjs", "tx.mjs", "fund.mjs", "constants.mjs"],
              "sell.mjs": ["wallets.mjs", "utils.mjs", "tx.mjs", "fund.mjs", "constants.mjs"],
              "drain.mjs": ["wallets.mjs", "fund.mjs"]}
    colors = {k: v[2] for v in scripts for k in [v[0]]}
    for src, dsts in edges1.items():
        sx, _, sb = P1[src]
        for d in dsts:
            dx, dt, _ = P2[d]
            my = (sb + dt) / 2
            s.line(f"M{sx:.1f} {sb+2} C{sx:.1f} {my} {dx:.1f} {my} {dx:.1f} {dt-4}", colors[src], "arrd", op=0.35, sw=1.2)
    edges2 = {"tx.mjs": ["@pump-fun/pump-sdk", "@solana/web3.js", "@solana/spl-token"],
              "jito.mjs": ["jito block engine", "bs58 · bn.js"],
              "wallets.mjs": ["bs58 · bn.js"], "utils.mjs": ["@solana/web3.js"], "fund.mjs": ["@solana/web3.js"]}
    for src, dsts in edges2.items():
        sx, _, sb = P2[src]
        for d in dsts:
            dx, dt, _ = P3[d]
            my = (sb + dt) / 2
            s.line(f"M{sx:.1f} {sb+2} C{sx:.1f} {my} {dx:.1f} {my} {dx:.1f} {dt-4}", NEON2, "arrd", op=0.3, sw=1.2)
    s.a('</g>')
    s.save("arch.svg")


# ===================================================================== terminal
def terminal():
    H = 470
    s = SVG(H, "apekit terminal output: bundle, sell, drain")
    s.a('<g filter="url(#glow)">')
    L = [("$ ", NEON, "npm run bundle -- DYdf…pump 4 0.34 jito", TXT),
         ("", None, "[apekit] bundler", NEON),
         ("", None, "  mint:     DYdfB51G…pump", MUT),
         ("", None, "  wallets:  4", MUT),
         ("", None, "  budget:   0.34 SOL", MUT),
         ("", None, "  mode:     jito", MUT),
         ("", None, "  master:   7xKXtg2C...", MUT),
         ("", None, "[phase 1] funding wallets...", TXT),
         ("", None, "[phase 1] funded 4/4", NEON2),
         ("", None, "[phase 2] buying (jito)...", TXT),
         ("", None, "[phase 2] priority fee: 42000 microLamports", MUT),
         ("", None, "[jito] bundle sent (attempt 1, tip 0.001 SOL)", CYN),
         ("", None, "[jito] bundle landed!", CYN),
         ("", None, "[phase 2] buys: 4/4", NEON),
         ("", None, "[apekit] wallet keys saved to data/wallets.json", DIM)]
    R = [("$ ", NEON, "npm run sell", TXT),
         ("", None, "[apekit] sell all", RED),
         ("", None, "  wallets: 4", MUT),
         ("", None, "[sold] 9pMHBgm2 tokens: 2871004113", TXT),
         ("", None, "[sold] HfQ29Lm4 tokens: 2790118320", TXT),
         ("", None, "[fund] 3sVrT1c9 — topping up for gas", ORG),
         ("", None, "[sold] 3sVrT1c9 tokens: 2702555190", TXT),
         ("", None, "[apekit] sold from 4/4 wallets", RED),
         ("", None, "", TXT),
         ("$ ", NEON, "npm run drain", TXT),
         ("", None, "[apekit] drain", MAG),
         ("", None, "  wallets: 4", MUT),
         ("", None, "[apekit] drained 4/4 wallets", MAG),
         ("", None, "[apekit] recovered ~0.3721 SOL", MAG),
         ("$ ", NEON, "", TXT)]
    s.panel(30, 64, 640, 380, [("● ", NEON), ("zsh ", NEON), (" bundle.mjs", TXT)], NEON)
    s.panel(690, 64, 540, 380, [("● ", RED), ("zsh ", RED), (" sell.mjs → drain.mjs", TXT)], RED)
    for col, lines in [(52, L), (712, R)]:
        for i, (p, pc, t, c) in enumerate(lines):
            parts = ([(p, pc)] if p else []) + [(t, c)]
            s.runs(col, 98 + i * 22.6, parts)
    s.a(f'<rect x="{712 + 2*CW:.1f}" y="{98 + 14*22.6 - 11}" width="8" height="14" fill="{NEON}"/>')
    s.runs(40, 40, [("live output", NEON), ("   log format taken from the scripts, values are an example", DIM)])
    s.a('</g>')
    s.save("terminal.svg")


# ===================================================================== jito vs staggered
def modes():
    H = 430
    s = SVG(H, "jito bundle vs staggered sends on the slot timeline")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("send modes", NEON), ("   same wallets, same buys, different footprint", MUT)])
    s.runs(W - 40, 40, [("1 slot ≈ 400ms", DIM)], anchor_end=True)
    x0, sw, n = 210, 64, 16
    def lane(y, title, sub, color, hits):
        s.runs(40, y + 20, [(title, color)], size=15)
        s.runs(40, y + 42, [(sub, MUT)])
        for i in range(n):
            x = x0 + i * sw
            s.a(f'<rect x="{x}" y="{y}" width="{sw-6}" height="88" rx="4" fill="{PANEL}" stroke="{BORDER}"/>')
            s.text_c(x + (sw - 6) / 2, y + 106, f"s+{i}", DIM, 11)
        for slot, stack in hits.items():
            x = x0 + slot * sw
            for j, (lab, c) in enumerate(stack):
                yy = y + 88 - 16 * (j + 1) - 2
                s.a(f'<rect x="{x+4}" y="{yy}" width="{sw-14}" height="13" rx="2" fill="{c}" fill-opacity="0.85"/>')
                s.text_c(x + (sw - 6) / 2, yy + 10.5, lab, BG1, 10)
    jito = {2: [("w01", BUY), ("w02", BUY), ("w03", BUY), ("w04", BUY), ("tip", CYN)]}
    lane(80, "JITO", "atomic bundle", CYN, jito)
    s.a(f'<rect x="{x0 + 2*sw - 4}" y="72" width="{sw+2}" height="104" rx="6" fill="none" stroke="{CYN}" stroke-dasharray="4 3"/>')
    s.runs(x0 + 3 * sw + 6, 112, [("◄ ", CYN), ("all 5 txs, one slot, one leader", TXT)])
    s.runs(x0 + 3 * sw + 6, 134, [("  ", CYN), ("lands together or not at all", MUT)])
    stag = {1: [("w01", BUY)], 7: [("w02", BUY)], 11: [("w03", BUY)], 15: [("w04", BUY)]}
    lane(240, "STAGGERED", "one tx at a time", ORG, stag)
    for a_, b_, lab in [(1, 7, "2.4s"), (7, 11, "1.7s"), (11, 15, "1.9s")]:
        xa, xb = x0 + a_ * sw + sw / 2, x0 + b_ * sw + sw / 2 - 6
        s.line(f"M{xa} 232 Q{(xa+xb)/2} 210 {xb} 232", ORG, "arr", op=0.7, dash="3 3")
        s.text_c((xa + xb) / 2, 212, lab, ORG, 11)
    s.runs(40, 395, [("jito ", CYN), ("→ ", DIM), ("one block, tip paid by master, 5 tries", MUT), ("     staggered ", ORG), ("→ ", DIM), ("random 2-5s gaps, no tip", MUT)])
    s.a('</g>')
    s.save("modes.svg")


# ===================================================================== tip ladder
def tips():
    H = 400
    s = SVG(H, "jito retry ladder: tip escalation per attempt")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("retry ladder", CYN), ("   tip = 0.001 × attempt, cap 0.01 SOL", MUT)])
    s.runs(W - 40, 40, [("poll 10 × 3s per attempt", DIM)], anchor_end=True)
    base_y, maxh = 300, 190
    bw, gap, x0 = 150, 46, 60
    for i in range(5):
        tip = 0.001 * (i + 1)
        h = maxh * tip / 0.005
        x = x0 + i * (bw + gap)
        c = grad([CYN, NEON], i / 4)
        s.a(f'<rect x="{x}" y="{base_y - h:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{c}" fill-opacity="0.18" stroke="{c}" stroke-opacity="0.9"/>')
        for k in range(int(h // 10)):
            s.a(f'<rect x="{x+8}" y="{base_y - 8 - k*10:.1f}" width="{bw-16}" height="6" fill="{c}" fill-opacity="0.75"/>')
        s.text_c(x + bw / 2, base_y - h - 14, f"{tip:.3f} SOL", c, 14)
        s.text_c(x + bw / 2, base_y + 24, f"attempt {i+1}", TXT)
        res = ("landed ✓", BUY) if i == 2 else ("miss · retry", DIM) if i < 2 else ("skipped", DIM)
        s.text_c(x + bw / 2, base_y + 44, res[0], res[1])
        if i < 4:
            s.line(f"M{x+bw+6} {base_y-20} L{x+bw+gap-6} {base_y-20}", DIM if i >= 2 else CYN, "arrd" if i >= 2 else "arrc", op=0.7)
    s.a(f'<line x1="40" y1="{base_y}" x2="{W-260}" y2="{base_y}" stroke="{BORDER}"/>')
    fx = x0 + 5 * (bw + gap) - 10
    s.box(fx, 150, 210, 110, ORG, op=0.7, dash="4 3")
    s.runs(fx + 16, 178, [("all 5 missed?", ORG)])
    s.runs(fx + 16, 202, [("→ individual sends", TXT)])
    s.runs(fx + 16, 224, [("  per wallet, with", MUT)])
    s.runs(fx + 16, 244, [("  priority fee", MUT)])
    s.runs(40, 372, [("each attempt: ", MUT), ("fresh blockhash", TXT), (" · ", DIM), ("rebuilt txs", TXT), (" · ", DIM), ("3 block engines", TXT), (" · ", DIM), ("random tip account (1 of 8)", TXT)])
    s.a('</g>')
    s.save("tips.svg")


# ===================================================================== wallet lifecycle
def lifecycle():
    H = 380
    s = SVG(H, "wallet lifecycle: fresh, funded, holding, sold, drained")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("wallet lifecycle", NEON), ("   what every generated keypair goes through", MUT)])
    s.runs(W - 40, 40, [("tracked in data/wallets.json", DIM)], anchor_end=True)
    states = [("FRESH", "Keypair.generate()", 0.0, 0.0, DIM, "bundle.mjs"),
              ("FUNDED", "master → wallet", 1.0, 0.0, NEON2, "fund.mjs"),
              ("HOLDING", "buy on curve", 0.12, 1.0, BUY, "tx.mjs"),
              ("SOLD", "sell 100%", 0.95, 0.0, RED, "sell.mjs"),
              ("DRAINED", "sweep → master", 0.03, 0.0, MAG, "drain.mjs")]
    bw, gap, x0, y0 = 206, 37, 40, 80
    for i, (name, d, sol, tok, c, src) in enumerate(states):
        x = x0 + i * (bw + gap)
        s.box(x, y0, bw, 210, c, op=0.8)
        s.corners(x, y0, bw, 210, c)
        s.runs(x + 16, y0 + 30, [(f"{i+1:02d} ", DIM), (name, c)], size=15)
        s.runs(x + 16, y0 + 54, [(d, MUT)])
        for j, (lab, v, cc) in enumerate([("SOL", sol, NEON2), ("TOK", tok, BUY)]):
            yy = y0 + 92 + j * 40
            s.runs(x + 16, yy, [(lab, DIM)])
            s.a(f'<rect x="{x+56}" y="{yy-11}" width="{bw-76}" height="12" fill="{BORDER}" fill-opacity="0.6"/>')
            if v > 0:
                s.a(f'<rect x="{x+56}" y="{yy-11}" width="{(bw-76)*v:.1f}" height="12" fill="{cc}" fill-opacity="0.85"/>')
        s.sep(x + 12, x + bw - 12, y0 + 162)
        s.runs(x + 16, y0 + 190, [("› ", c), (src, TXT)])
        if i < 4:
            s.line(f"M{x+bw+4} {y0+105} L{x+bw+gap-4} {y0+105}", c)
    s.runs(40, 340, [("fee reserve ", MUT), ("0.01 SOL", TXT), (" stays during buys", DIM), ("     sell tops up gas ", MUT), ("if a wallet runs dry", DIM), ("     drain keeps ", MUT), ("5000 lamports", TXT), (" for the fee", DIM)])
    s.a('</g>')
    s.save("lifecycle.svg")


# ===================================================================== config panel
def config():
    H = 350
    s = SVG(H, "apekit config: bundle and volume arguments")
    s.a('<g filter="url(#glow)">')
    s.runs(40, 40, [("control panel", NEON), ("   positional args, defaults shown", MUT)])
    def card(x, w, title, color, cmd, rows):
        s.panel(x, 76, w, 244, [("● ", color), (title, color)], color)
        s.runs(x + 20, 110, [("$ ", NEON), (cmd, TXT)])
        for i, (k, v, frac, note) in enumerate(rows):
            y = 150 + i * 46
            s.runs(x + 20, y, [(k, MUT)])
            s.runs(x + w - 20, y, [(v, TXT)], anchor_end=True)
            tx, tw = x + 20, w - 40
            s.a(f'<rect x="{tx}" y="{y+10}" width="{tw}" height="4" rx="2" fill="{BORDER}"/>')
            if frac is not None:
                s.a(f'<rect x="{tx}" y="{y+10}" width="{tw*frac:.1f}" height="4" rx="2" fill="{color}"/>')
                s.a(f'<rect x="{tx + tw*frac - 5:.1f}" y="{y+5}" width="10" height="14" rx="2" fill="{PALE}" stroke="{color}"/>')
            else:
                s.runs(tx, y + 22, [(note, DIM)])
    card(40, 570, "bundle.mjs", CYN, "npm run bundle -- <MINT> 4 0.5 jito",
         [("MINT", "token mint", None, ""), ("wallets", "5", 0.25, ""), ("budget", "0.5 SOL", 0.3, ""),
          ("mode", "jito | staggered", None, "")])
    card(650, 570, "volume.mjs", LIME, "npm run volume -- <MINT> 12 0.5 15 0.65",
         [("wallets", "12", 0.45, ""), ("budget", "0.5 SOL", 0.3, ""), ("duration", "15 min", 0.35, ""),
          ("buy_bias", "0.65", 0.65, "")])
    s.a('</g>')
    s.save("config.svg")

if __name__ == "__main__":
    hero(); divider(); flow(); volume(); arch(); terminal(); modes(); tips(); lifecycle(); config()
    for sec in SECTIONS:
        section(*sec)
