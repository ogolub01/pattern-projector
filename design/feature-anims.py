"""Builds the six feature animations for the landing page (SVG + SMIL), printed as one HTML <section>.
Run: python3 design/feature-anims.py > /tmp/feats.html, then paste between the FEATURES markers in public/index.html.
Colours match the projector screen: near-black mat, ink-white lines, brass accents, red calibration corners."""

BG, INK, BR, RED, DIM = '#0A0A09', '#EDEAE2', '#C9A24B', '#FF6B5E', '#6E6B64'
EASE = '.45 0 .2 1'

def anim(attr, values, times, dur, extra=''):
    n = len(values) - 1
    return (f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="{";".join(str(t) for t in times)}" keySplines="{";".join([EASE] * n)}" '
            f'values="{";".join(str(v) for v in values)}"{extra}/>')

def anim_t(kind, values, times, dur, additive=False):
    n = len(values) - 1
    add = ' additive="sum"' if additive else ''
    return (f'<animateTransform attributeName="transform" type="{kind}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="{";".join(str(t) for t in times)}" keySplines="{";".join([EASE] * n)}" values="{";".join(values)}"{add}/>')

def svg(body, label):
    return (f'<svg viewBox="0 0 400 300" role="img" aria-label="{label}">'
            f'<rect width="400" height="300" fill="{BG}"/><rect width="400" height="300" fill="url(#fg1)"/><rect width="400" height="300" fill="url(#fg5)"/>'
            f'{body}</svg>')

def pts(p): return ' '.join(f'{x:.1f},{y:.1f}' for x, y in p)
def path(p, close=True): return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in p) + (' Z' if close else '')

# ---------- 1. calibrate: drag corner C onto the mat corner, the grid straightens ----------
def calibrate():
    T = 6
    A, B, D = (70, 55), (330, 55), (70, 245)
    C1, C0 = (330, 245), (356, 222)            # where C ends (the mat corner) and where it starts (off)
    def bil(u, v, C):
        top = (A[0] + (B[0] - A[0]) * u, A[1] + (B[1] - A[1]) * u)
        bot = (D[0] + (C[0] - D[0]) * u, D[1] + (C[1] - D[1]) * u)
        return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)
    times = [0, .22, .62, .9, 1]
    out = []
    # the real mat: a dim dashed outline with corner crosses
    out.append(f'<rect x="70" y="55" width="260" height="190" fill="none" stroke="{DIM}" stroke-width="1.2" stroke-dasharray="4 5"/>')
    for (x, y) in [A, B, C1, D]:
        out.append(f'<path d="M{x-7} {y}h14M{x} {y-7}v14" stroke="{DIM}" stroke-width="1.2"/>')
    # projected grid
    lines = []
    for k in range(9):
        u = k / 8; lines.append([(u, 0), (u, 1)])
    for k in range(7):
        v = k / 6; lines.append([(0, v), (1, v)])
    for ln in lines:
        d0 = path([bil(u, v, C0) for u, v in ln], False); d1 = path([bil(u, v, C1) for u, v in ln], False)
        edge = (ln[0][0] == ln[1][0] and ln[0][0] in (0, 1)) or (ln[0][1] == ln[1][1] and ln[0][1] in (0, 1))
        sw, op = (1.6, .9) if edge else (1, .38)
        out.append(f'<path d="{d0}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-opacity="{op}">'
                   + anim('d', [d0, d0, d1, d1, d0], times, T) + '</path>')
    # corner handles (A, B, D fixed; C dragged, brass while held)
    for (x, y), L in [(A, 'A'), (B, 'B'), (D, 'D')]:
        ly = y - 15 if L in 'AB' else y + 23
        out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{RED}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="1.8" fill="{RED}"/>'
                   f'<text x="{x}" y="{ly}" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="{RED}">{L}</text>')
    cx = anim('cx', [C0[0], C0[0], C1[0], C1[0], C0[0]], times, T); cy = anim('cy', [C0[1], C0[1], C1[1], C1[1], C0[1]], times, T)
    col = f'<animate attributeName="stroke" dur="{T}s" repeatCount="indefinite" keyTimes="0;.18;.66;1" values="{RED};{BR};{RED};{RED}" calcMode="discrete"/>'
    out.append(f'<circle r="9" fill="none" stroke="{RED}" stroke-width="2.4">{cx}{cy}{col}</circle>')
    out.append(f'<circle r="20" fill="{BR}" fill-opacity=".14">{cx}{cy}' + anim('r', [0, 20, 20, 0, 0], [0, .2, .62, .7, 1], T) + '</circle>')
    tx = anim('x', [C0[0], C0[0], C1[0], C1[0], C0[0]], times, T); ty = anim('y', [C0[1] + 23, C0[1] + 23, C1[1] + 23, C1[1] + 23, C0[1] + 23], times, T)
    out.append(f'<text text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="{RED}">{tx}{ty}C</text>')
    out.append(f'<text x="200" y="285" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" fill="{BR}" opacity="0">'
               + anim('opacity', [0, 0, 1, 1, 0], [0, .64, .7, .9, 1], T) + 'Grid matches the mat · true size</text>')
    return svg(''.join(out), 'A corner of the projected grid being dragged onto the corner of the cutting mat until the grid is square')

# ---------- 2. fill: tap inside a piece, the fill spreads to its cutting line ----------
def fill():
    T = 6
    piece = [(96, 70), (214, 62), (232, 118), (226, 238), (104, 240), (88, 150)]
    nb = [(246, 58), (330, 64), (322, 236), (240, 240), (250, 150)]   # neighbouring piece, left unfilled
    d, dn = path(piece), path(nb)
    out = [f'<defs><clipPath id="fpc"><path d="{d}"/></clipPath></defs>',
           f'<path d="{dn}" fill="none" stroke="{INK}" stroke-width="1.8"/>',
           f'<path d="M110 196 H208" stroke="{INK}" stroke-opacity=".5" stroke-width="1"/>',      # a line inside the piece (hem line)
           f'<g clip-path="url(#fpc)"><circle cx="150" cy="150" r="0" fill="{BR}" fill-opacity=".3">'
           + anim('r', [0, 0, 190, 190, 190], [0, .22, .52, .9, 1], T) + anim('fill-opacity', [.3, .3, .3, .3, 0], [0, .22, .52, .9, 1], T) + '</circle></g>',
           f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2"><animate attributeName="stroke" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.5;.92" values="{INK};{BR};{INK}"/>'
           + anim('stroke-width', [2, 2, 3, 3, 2], [0, .48, .54, .9, 1], T) + '</path>',
           f'<circle cx="150" cy="150" r="4" fill="none" stroke="{INK}" stroke-width="2">' + anim('r', [4, 4, 22, 22, 4], [0, .12, .26, .99, 1], T)
           + anim('opacity', [0, 1, 0, 0, 0], [0, .12, .26, .99, 1], T) + '</circle>',
           f'<circle cx="150" cy="150" r="3.5" fill="{INK}" opacity="0">' + anim('opacity', [0, 0, 1, 0, 0], [0, .1, .13, .22, 1], T) + '</circle>',
           f'<text x="160" y="128" text-anchor="middle" font-family="Bodoni Moda, Georgia, serif" font-style="italic" font-size="19" fill="{BR}" opacity="0">'
           + anim('opacity', [0, 0, 1, 1, 0], [0, .56, .62, .9, 1], T) + 'Front</text>',
           f'<text x="200" y="285" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" fill="{DIM}">tap inside · stops at the cutting line</text>']
    return svg(''.join(out), 'A tap inside a pattern piece fills it up to its cutting line without spilling into the piece next to it')

# ---------- 3. dim what's cut: tick a piece and it dims on the mat ----------
def dim():
    T = 6
    sleeve = 'M222 120 C 235 118, 244 70, 268 68 C 292 70, 301 118, 314 120 L 304 230 L 232 230 Z'
    front = path([(328, 60), (386, 56), (390, 238), (332, 242)])
    back = path([(136, 60), (204, 56), (212, 236), (140, 240)])
    rows = [('Back', 70), ('Sleeve', 98), ('Front', 126)]
    out = [f'<path d="{back}" fill="none" stroke="{INK}" stroke-width="1.8" opacity=".22"/>',
           f'<path d="{front}" fill="none" stroke="{INK}" stroke-width="1.8"/>',
           f'<path d="{sleeve}" fill="none" stroke="{INK}" stroke-width="1.8">' + anim('opacity', [1, 1, .22, .22, 1], [0, .36, .5, .9, 1], T) + '</path>',
           # a small pieces list, as in the panel
           f'<rect x="150" y="248" width="0" height="0"/>']
    lst = [f'<g transform="translate(12 150)"><rect width="108" height="100" fill="#0E0E0D" stroke="#2A2926"/>'
           f'<text x="10" y="18" font-family="IBM Plex Mono, monospace" font-size="9" fill="{DIM}" letter-spacing="1">PATTERN PIECES</text>']
    for i, (name, _) in enumerate(rows):
        y = 34 + i * 22
        done = name == 'Back'
        lst.append(f'<rect x="10" y="{y}" width="12" height="12" fill="{BR if done else "none"}" stroke="{BR if done else DIM}"/>')
        if done: lst.append(f'<path d="M12.5 {y+6} l3 3 5-6" fill="none" stroke="{BG}" stroke-width="1.6"/>')
        if name == 'Sleeve':
            lst.append(f'<rect x="10" y="{y}" width="12" height="12" fill="{BR}" opacity="0">' + anim('opacity', [0, 0, 1, 1, 0], [0, .3, .34, .9, 1], T) + '</rect>'
                       f'<path d="M12.5 {y+6} l3 3 5-6" fill="none" stroke="{BG}" stroke-width="1.6" opacity="0">' + anim('opacity', [0, 0, 1, 1, 0], [0, .3, .34, .9, 1], T) + '</path>'
                       f'<circle cx="16" cy="{y+6}" r="3" fill="none" stroke="{INK}" opacity="0">' + anim('r', [3, 3, 16, 16, 3], [0, .26, .36, .99, 1], T) + anim('opacity', [0, 1, 0, 0, 0], [0, .26, .36, .99, 1], T) + '</circle>')
        op = '.45' if done else '1'
        dec = ' text-decoration="line-through"' if done else ''
        t = f'<text x="30" y="{y+10}" font-family="Bodoni Moda, Georgia, serif" font-style="italic" font-size="13" fill="{INK}" opacity="{op}"{dec}>'
        if name == 'Sleeve': t += anim('opacity', [1, 1, .45, .45, 1], [0, .34, .4, .9, 1], T)
        lst.append(t + name + '</text>')
    lst.append('</g>')
    out = out[:3] + lst
    return svg(''.join(out), 'Ticking a piece off in the pieces list dims it on the mat, so the pieces still to cut stand out')

# ---------- 4. move one piece on its own ----------
def single():
    T = 7
    sel = 'M-40 -55 C -30 -57, -22 -92, 0 -94 C 22 -92, 30 -57, 40 -55 L 32 55 L -32 55 Z'
    others = [path([(36, 56), (110, 52), (118, 150), (40, 154)]), path([(250, 50), (360, 46), (366, 150), (256, 152)]),
              path([(150, 176), (240, 172), (246, 236), (154, 240)])]
    out = [f'<path d="M20 266 H380" stroke="{BR}" stroke-width="1.4" stroke-dasharray="6 5" opacity=".7"/>',
           f'<text x="380" y="284" text-anchor="end" font-family="IBM Plex Mono, monospace" font-size="10" fill="{DIM}">selvedge</text>']
    for o in others:
        out.append(f'<path d="{o}" fill="none" stroke="{INK}" stroke-width="1.8">' + anim('opacity', [1, 1, 0, 0, 1], [0, .2, .32, .88, 1], T) + '</path>')
    tr = anim_t('translate', ['178 110', '178 110', '178 110', '262 196', '262 196', '178 110'], [0, .3, .36, .7, .88, 1], T)
    ro = anim_t('rotate', ['-28', '-28', '-28', '0', '0', '-28'], [0, .3, .36, .7, .88, 1], T, additive=True)
    col = f'<animate attributeName="stroke" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.14;.9" values="{INK};{BR};{INK}"/>'
    out.append(f'<g>{tr}{ro}<path d="{sel}" fill="none" stroke="{INK}" stroke-width="2.2">{col}</path>'
               f'<path d="M0 -70 V 40 M-6 -62 L0 -70 L6 -62 M-6 32 L0 40 L6 32" fill="none" stroke="{BR}" stroke-width="1.6" opacity=".9"/></g>')
    out.append(f'<text x="200" y="26" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" fill="{BR}" opacity="0">'
               + anim('opacity', [0, 0, 1, 1, 0], [0, .3, .36, .86, .9], T) + 'Sleeve · on its own</text>')
    return svg(''.join(out), 'One piece is picked out, the others fade away, and it is turned and moved into place along the fabric edge')

# ---------- 5. mirror on fold: draw along the centre front and the other half appears ----------
def mirror():
    T = 6
    fx = 200
    half = ('M200 92 C 214 92, 228 80, 232 62 L 292 76 C 288 108, 292 128, 306 140 L 300 232 C 266 236, 232 238, 200 238 Z'
            'M240 237 L248 175 L256 236')
    out = [f'<path d="{half}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>',
           f'<g transform="translate({fx} 0)"><g>' + anim_t('scale', ['0.001 1', '0.001 1', '-1 1', '-1 1', '0.001 1'], [0, .3, .62, .9, 1], T)
           + f'<g transform="translate({-fx} 0)"><path d="{half}" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity=".7" stroke-linejoin="round"/></g></g></g>',
           f'<path d="M200 70 V 258" stroke="{BR}" stroke-width="2" stroke-dasharray="7 6"/>',
           f'<text x="208" y="268" font-family="IBM Plex Mono, monospace" font-size="10" fill="{BR}">centre front · fold</text>',
           f'<text x="200" y="40" text-anchor="middle" font-family="Bodoni Moda, Georgia, serif" font-style="italic" font-size="19" fill="{BR}" opacity="0">'
           + anim('opacity', [0, 0, 1, 1, 0], [0, .62, .68, .9, 1], T) + 'Whole front</text>']
    return svg(''.join(out), 'Half a bodice front with its centre front on the fold; the other half is mirrored across the fold to make the whole front')

# ---------- 6. quiet: the projection blacks out, a tap brings it back ----------
def quiet():
    T = 6
    ui = (f'<rect x="12" y="14" width="96" height="200" fill="#0E0E0D" stroke="#2A2926"/>'
          f'<text x="22" y="40" font-family="Bodoni Moda, Georgia, serif" font-style="italic" font-size="16" fill="{INK}">Pattern</text>'
          + ''.join(f'<rect x="22" y="{56 + i * 26}" width="{76 - (i % 2) * 18}" height="12" fill="none" stroke="#2A2926"/>' for i in range(5))
          + f'<rect x="362" y="40" width="26" height="170" fill="#0E0E0D" stroke="#2A2926"/>'
          + ''.join(f'<circle cx="375" cy="{58 + i * 26}" r="5" fill="none" stroke="{DIM}"/>' for i in range(6)))
    pat = (f'<path d="M140 120 C 158 118, 170 66, 200 64 C 230 66, 242 118, 260 120 L 248 238 L 152 238 Z" fill="none" stroke="{INK}" stroke-width="2"/>'
           f'<path d="M200 82 V 220" stroke="{BR}" stroke-width="1.4"/>')
    cover = (f'<rect width="400" height="300" fill="#000" opacity="0">' + anim('opacity', [0, 0, 1, 1, 0, 0], [0, .26, .38, .72, .8, 1], T) + '</rect>'
             f'<text x="200" y="272" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="2" fill="#3A3935" opacity="0">'
             + anim('opacity', [0, 0, 1, 1, 0, 0], [0, .36, .42, .58, .68, 1], T) + 'QUIET · TAP TO RETURN</text>'
             f'<circle cx="230" cy="170" r="4" fill="none" stroke="{INK}" stroke-width="2" opacity="0">' + anim('r', [4, 4, 22, 22], [0, .7, .8, 1], T)
             + anim('opacity', [0, 0, .9, 0, 0], [0, .69, .7, .8, 1], T) + '</circle>')
    return svg(ui + pat + cover, 'The projection fades to black so the fabric can be seen on its own, and a tap brings the pattern back')

FEATS = [
    ('Line it up with your mat', calibrate,
     'Drag the four corners of the grid onto the corners of your mat and that’s it. Ten centimetres on the pattern is ten centimetres on the mat, even if your projector sits a bit wonky. It remembers, so next time you can get straight to sewing.'),
    ('Tap to mark a piece', fill,
     'Tap inside a pattern piece and it fills right up to the cutting line, notches and all, without spilling into the piece next door. Give it a name and it’s saved with your pattern.'),
    ('Cut pieces fade away', dim,
     'Tick a piece off once it’s cut and it goes dim, so you can see what’s left. Nothing gets cut twice, or forgotten (which is more my style).'),
    ('Move one piece at a time', single,
     'Pick a piece and the rest step aside, so you can shuffle just that one around your fabric until it fits.'),
    ('Open out the fold', mirror,
     'For a piece cut on the fold, draw along the fold line and Notch mirrors the other half, so you see the whole piece. Handy for cutting on a single layer, or placing a print just where you want it.'),
    ('Hide it for a moment', quiet,
     'One tap and the pattern fades away, so you can see the actual fabric, check a chalk mark or how a print falls. Tap again and it’s back.'),
]

print('<section class="wrap feats" aria-labelledby="featsT">')
print('  <h2 id="featsT">A few things it does</h2>')
print('  <svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
      '<pattern id="fg1" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#EDEAE2" stroke-opacity=".06"/></pattern>'
      '<pattern id="fg5" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="#EDEAE2" stroke-opacity=".14"/></pattern>'
      '</defs></svg>')
print('  <div class="featgrid">')
STILL = {'calibrate': 4.8, 'fill': 4.5, 'dim': 4.5, 'single': 5.6, 'mirror': 4.5, 'quiet': 0}
for title, fn, text in FEATS:
    print(f'    <article class="feat" data-still="{STILL[fn.__name__]}"><figure>{fn()}</figure><h3>{title}</h3><p>{text}</p></article>')
print('  </div>')
print('</section>')
