#!/usr/bin/env python3
"""Gera giyu-contributions.svg: um Giyu em pixel art corta seus quadradinhos de contribuição.
Só usa a biblioteca padrão do Python. Lê o calendário público do GitHub (sem token)."""
import os, re, sys, datetime, urllib.request

USER = os.environ.get("GH_USER", "gustavosp4591-lab")
OUT = os.environ.get("OUT", "dist/giyu-contributions.svg")

def buscar(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    dias = {}
    for t in re.finditer(r'<(?:td|rect)\b[^>]*data-date="[^"]+"[^>]*>', html):
        tag = t.group(0)
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        l = re.search(r'data-level="(\d)"', tag)
        if d and l:
            dias[d.group(1)] = int(l.group(1))
    if not dias:
        raise RuntimeError("não encontrei o calendário de contribuições")
    return dias

# ---------- pixel art do Giyu (16 x 23) ----------
PAL = {"K": "#0D0D14", "H": "#262640", "S": "#F2C9A6", "E": "#3D8BFF", "W": "#E8EAF2",
       "R": "#C2183A", "G": "#1FB574", "Y": "#FFB82E", "T": "#E8B93C", "B": "#D5ECFF", "b": "#7DB8F5", "L": "#1A1A26"}
CORPO = [
"......KKKK......",
".....KKKKKK.....",
"....KKKKKKKK....",
"....KKHKKKHK....",
"...KKSSSSSSKK...",
"...KKSSSSSESK...",
"...KKSSSSSSSK...",
"....KKSSSSSK....",
".....KWWWWK.....",
"..RRRKKKKGYGY...",
"..RRRKKKKYGYG...",
"..RRRKKKKGYGY...",
"..RRRKKKKYGYG...",
"..RRRKKKKGYGY...",
"..RRKKKKKKYGY...",
"..RRKKKKKKKKK...",
"...RKKKKKKKKK...",
]
PERNAS_A = ["....KKK..KKK....","....KKK..KKK....","...KKK....KKK...","...KKK....KKK...","..LLLL....LLLL.."]
PERNAS_B = ["....KKKKKKK.....","....KKKKKKK.....","....KKK.KKK.....","....KKK.KKK.....","...LLLL.LLLL...."]

def runs(linhas, y0):
    out = []
    for dy, ln in enumerate(linhas):
        x = 0
        while x < len(ln):
            c = ln[x]
            if c == ".":
                x += 1; continue
            j = x
            while j < len(ln) and ln[j] == c:
                j += 1
            out.append(f'<rect x="{x}" y="{y0+dy}" width="{j-x}" height="1" fill="{PAL[c]}"/>')
            x = j
    return "".join(out)

def sprite_svg():
    corpo = runs(CORPO, 0)
    pa = runs(PERNAS_A, len(CORPO)); pb = runs(PERNAS_B, len(CORPO))
    espada = ('<rect x="0" y="-1" width="1" height="3" fill="#E8B93C"/><rect x="1" y="0" width="10" height="1" fill="#D5ECFF"/>'
              '<rect x="1" y="1" width="10" height="1" fill="#7DB8F5"/><rect x="11" y="0" width="1" height="1" fill="#fff"/>')
    return corpo, pa, pb, espada

def gerar(dias):
    datas = sorted(dias)
    ini = datetime.date.fromisoformat(datas[0])
    ini -= datetime.timedelta(days=(ini.weekday() + 1) % 7)       # domingo da primeira semana
    cel = []
    for ds in datas:
        d = datetime.date.fromisoformat(ds)
        col = (d - ini).days // 7
        lin = (d.weekday() + 1) % 7
        cel.append((col, lin, dias[ds]))
    ncol = max(c for c, _, _ in cel) + 1
    C, STEP, X0, Y0 = 11, 14, 28, 44
    W = X0 * 2 + ncol * STEP
    H = Y0 + 7 * STEP + 40
    CORES = ["#16213F", "#1D3F8A", "#2F6FD6", "#5DA0FF", "#BFE0FF"]
    LOOP, RUN = 14.0, 10.0
    span = W + 120
    css_cel, svg_cel = [], []
    for col in range(ncol):
        xc = X0 + col * STEP + C / 2
        t = max(0.0, (xc - 4) / span * RUN)
        p = t / LOOP * 100
        css_cel.append(f"@keyframes k{col}{{0%,{p-0.3:.2f}%{{opacity:1;transform:none;fill:var(--f)}}{p:.2f}%{{opacity:1;transform:scale(1.5,.18) rotate(-35deg);fill:#fff}}"
                       f"{p+1.4:.2f}%{{opacity:0;transform:translate(7px,-9px) scale(.1) rotate(-35deg)}}88%{{opacity:0;transform:none}}96%{{opacity:1;transform:none;fill:var(--f)}}100%{{opacity:1;transform:none;fill:var(--f)}}}}"
                       f".k{col}{{animation:k{col} {LOOP}s linear infinite}}")
    for col, lin, nivel in cel:
        x = X0 + col * STEP; y = Y0 + lin * STEP
        if nivel == 0:
            svg_cel.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="2" fill="{CORES[0]}"/>')
        else:
            svg_cel.append(f'<rect class="c k{col}" style="--f:{CORES[nivel]}" x="{x}" y="{y}" width="{C}" height="{C}" rx="2" fill="{CORES[nivel]}"/>')
    corpo, pa, pb, espada = sprite_svg()
    P = 4
    gy = Y0 + 7 * STEP + 14 - (len(CORPO) + 5) * P          # pés um pouco abaixo da grade
    css = f"""<style>
    .c{{transform-box:fill-box;transform-origin:center}}
    {''.join(css_cel)}
    .run{{animation:run {LOOP}s linear infinite}}
    @keyframes run{{0%{{transform:translateX(-80px);opacity:1}}{RUN/LOOP*100:.2f}%{{transform:translateX({W+40}px);opacity:1}}{RUN/LOOP*100+1:.2f}%{{opacity:0}}99.9%{{opacity:0;transform:translateX(-80px)}}100%{{opacity:1;transform:translateX(-80px)}}}}
    .bob{{animation:bob .36s steps(1) infinite}}@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}
    .fa{{animation:fa .36s steps(1) infinite}}@keyframes fa{{0%{{opacity:1}}50%{{opacity:0}}}}
    .fb{{animation:fb .36s steps(1) infinite}}@keyframes fb{{0%{{opacity:0}}50%{{opacity:1}}}}
    .sw{{animation:sw 1.2s ease-in-out infinite}}@keyframes sw{{0%,55%{{transform:rotate(-50deg)}}75%{{transform:rotate(30deg)}}100%{{transform:rotate(-50deg)}}}}
    .arc{{animation:arc 1.2s linear infinite;opacity:0}}@keyframes arc{{0%,60%{{opacity:0}}70%{{opacity:.95}}85%,100%{{opacity:0}}}}
    @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.run{{transform:translateX(24px)}}}}
  </style>"""
    marcas = "".join(f'<text x="{X0+c*STEP}" y="{Y0-8}" font-family="Courier New, monospace" font-size="10" fill="#4B6291">{m}</text>' for c, m in meses(ini, ncol))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Giyu em pixel art correndo pelo gráfico de contribuições do GitHub e cortando cada dia com a espada">
  <title>Giyu cortando as contribuições</title>{css}
  <rect width="{W}" height="{H}" rx="10" fill="#0B1428" stroke="#1D3566" stroke-width="1.5"/>
  <rect x="0" y="0" width="10" height="{H}" fill="#C2183A"/>
  <text x="{X0}" y="26" font-family="Courier New, monospace" font-size="14" letter-spacing="4" fill="#3D8BFF">// CONTRIBUIÇÕES · RESPIRAÇÃO DA ÁGUA</text>
  {marcas}
  {''.join(svg_cel)}
  <g class="run"><g transform="translate(0,{gy})" shape-rendering="crispEdges"><g class="bob"><g transform="scale({P})">
    <g class="fa">{pa}</g><g class="fb">{pb}</g>{corpo}
    <g transform="translate(12,12)"><g class="sw">{espada}<path class="arc" d="M2,-12 Q16,0 2,12" fill="none" stroke="#DDF0FF" stroke-width="1.2"/></g></g>
  </g></g></g></g>
</svg>
'''
    return svg

def meses(ini, ncol):
    nomes = ["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"]
    out, ult = [], -1
    for c in range(ncol):
        d = ini + datetime.timedelta(days=c * 7)
        if d.month != ult and d.day <= 14 or c == 0:
            out.append((c, nomes[d.month - 1])); ult = d.month
    return out

if __name__ == "__main__":
    dias = buscar(USER)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(gerar(dias))
    print(f"ok: {OUT} ({len(dias)} dias)")
