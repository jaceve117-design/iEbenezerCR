# -*- coding: utf-8 -*-
"""
Portadas de sección para Ministerios Ebenezer C.R.

Seis composiciones geométricas abstractas en un mismo idioma visual:
tierra cálida oscura, trazo de oro fino, halo de luz y viñeta. Cada una
lleva un motivo distinto ligado a su sección. Sin fotos y sin personas.

Se componen a 2x y se reducen, para que el trazo quede limpio.
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os, sys

W, H = 1400, 2000
SS = 2
w, h = W*SS, H*SS

ORO       = (212, 166, 90)
ORO_VIVO  = (247, 214, 148)
ORO_TENUE = (150, 112, 58)


# ── primitivas ────────────────────────────────────────────────────
def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))


def tierra(top, bot, brillo, gx, gy, gr, intensidad=2.1):
    """Degradado vertical + halo radial cálido."""
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(0, h, 2):
        c = _lerp(top, bot, y/h)
        d.rectangle([0, y, w, y+2], fill=c)
    cap = Image.new('L', (w, h), 0)
    dc = ImageDraw.Draw(cap)
    for i in range(80, 0, -1):
        r = gr*i/80
        dc.ellipse([gx-r, gy-r*0.85, gx+r, gy+r*0.85],
                   fill=int(255*(1-i/80)**intensidad))
    cap = cap.filter(ImageFilter.GaussianBlur(w*0.06))
    return Image.composite(Image.new('RGB', (w, h), brillo), im, cap)


def capa():
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def fundir(base, cap, desenfoque=0):
    if desenfoque:
        cap = cap.filter(ImageFilter.GaussianBlur(desenfoque))
    return Image.alpha_composite(base.convert('RGBA'), cap).convert('RGB')


def vineta(im, fuerza=0.5):
    cap = Image.new('L', (w, h), 0)
    ImageDraw.Draw(cap).ellipse([-w*0.3, -h*0.15, w*1.3, h*1.15], fill=255)
    cap = cap.filter(ImageFilter.GaussianBlur(w*0.1))
    return Image.composite(im, Image.blend(im, Image.new('RGB', (w, h)), fuerza), cap)


def grano(im, cantidad=0.022):
    return Image.blend(im, Image.effect_noise((w, h), 14).convert('RGB'), cantidad)


def acabar(im, nombre, destino):
    im = grano(vineta(im, 0.46))
    im = im.resize((W, H), Image.LANCZOS)
    ruta = os.path.join(destino, nombre + '.webp')
    im.save(ruta, 'WEBP', quality=84, method=6)
    print(f'  {nombre:<14} {os.path.getsize(ruta)//1024:>4} KB')
    return im


# ── 01 · SERVICIOS — la semana que converge ───────────────────────
def servicios(dest):
    im = tierra((15, 12, 10), (46, 33, 19), (128, 92, 40), w*.5, h*.44, w*1.0)
    cx, cy = w*.5, h*.5
    c = capa(); d = ImageDraw.Draw(c)
    # cuatro radios marcados: los cuatro servicios de la semana
    for i in range(4):
        a = math.radians(-90 + i*90 + 45)
        d.line([(cx, cy), (cx+math.cos(a)*h, cy+math.sin(a)*h)],
               fill=ORO+(120,), width=int(w*.004))
    # radios finos de fondo
    for i in range(48):
        a = math.radians(i*7.5)
        d.line([(cx, cy), (cx+math.cos(a)*h, cy+math.sin(a)*h)],
               fill=ORO_TENUE+(38,), width=int(w*.0014))
    im = fundir(im, c)
    # anillos concéntricos
    c = capa(); d = ImageDraw.Draw(c)
    for k in range(1, 9):
        r = w*.075*k
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ORO+(int(190*(1-k/10)),),
                  width=int(w*.0032))
    im = fundir(im, c)
    # núcleo luminoso
    c = capa(); d = ImageDraw.Draw(c)
    r = w*.055
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=ORO_VIVO+(210,))
    im = fundir(im, c, w*.012)
    return acabar(im, 'servicios', dest)


# ── 02 · HISTORIA — arquería que se aleja ─────────────────────────
def historia(dest):
    im = tierra((14, 12, 11), (42, 30, 18), (122, 86, 38), w*.5, h*.40, w*.95)
    c = capa(); d = ImageDraw.Draw(c)
    base, cx = h*.78, w*.5
    for k in range(9):
        r = w*.088*(k+1)
        a = int(215*(1-k/9)**1.3)
        g = max(1, int(w*.006*(1-k/16)))
        d.arc([cx-r, base-r, cx+r, base+r], 180, 360, fill=ORO+(a,), width=g)
        for x in (cx-r, cx+r):
            d.line([(x, base), (x, h)], fill=ORO+(int(a*.5),), width=g)
    im = fundir(im, c)
    # suelo
    c = capa(); ImageDraw.Draw(c).line([(0, base), (w, base)],
                                       fill=ORO+(70,), width=int(w*.002))
    return acabar(fundir(im, c), 'historia', dest)


# ── 03 · DEPARTAMENTOS — seis cuerpos, un sistema ─────────────────
def departamentos(dest):
    im = tierra((13, 12, 12), (34, 30, 24), (104, 88, 52), w*.5, h*.5, w*.9, 2.4)
    cx, cy, R = w*.5, h*.5, w*.30
    nodos = [(cx+math.cos(math.radians(-90+i*60))*R,
              cy+math.sin(math.radians(-90+i*60))*R) for i in range(6)]
    # cada nodo con todos los demás
    c = capa(); d = ImageDraw.Draw(c)
    for i in range(6):
        for j in range(i+1, 6):
            d.line([nodos[i], nodos[j]], fill=ORO+(58,), width=int(w*.0018))
    for n in nodos:
        d.line([(cx, cy), n], fill=ORO+(120,), width=int(w*.003))
    im = fundir(im, c)
    # hexágono exterior
    c = capa(); d = ImageDraw.Draw(c)
    d.polygon(nodos, outline=ORO+(150,), width=int(w*.0035))
    for n in nodos:
        r = w*.026
        d.ellipse([n[0]-r, n[1]-r, n[0]+r, n[1]+r], fill=(18, 15, 12, 255),
                  outline=ORO_VIVO+(235,), width=int(w*.004))
    r = w*.017
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=ORO_VIVO+(255,))
    return acabar(fundir(im, c), 'departamentos', dest)


# ── 04 · EN VIVO — la señal que se propaga ────────────────────────
def envivo(dest):
    im = tierra((16, 11, 11), (48, 26, 22), (140, 70, 52), w*.5, h*.34, w*.9)
    cx, cy = w*.5, h*.34
    c = capa(); d = ImageDraw.Draw(c)
    # arcos de emisión hacia abajo
    for k in range(1, 11):
        r = w*.085*k
        a = int(200*(1-k/11)**1.15)
        d.arc([cx-r, cy-r, cx+r, cy+r], 12, 168, fill=ORO+(a,), width=int(w*.0042))
    im = fundir(im, c)
    # foco
    c = capa(); d = ImageDraw.Draw(c)
    for rr, aa in ((w*.052, 90), (w*.030, 255)):
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=ORO_VIVO+(aa,))
    im = fundir(im, c, w*.006)
    # mástil
    c = capa(); ImageDraw.Draw(c).line([(cx, cy), (cx, h*.93)],
                                       fill=ORO+(130,), width=int(w*.0035))
    return acabar(fundir(im, c), 'envivo', dest)


# ── 05 · RECURSOS — el libro abierto ──────────────────────────────
def recursos(dest):
    im = tierra((13, 12, 11), (38, 31, 21), (116, 92, 48), w*.5, h*.40, w*.92)
    cx, cy = w*.5, h*.53
    AN, AL, CANTO = w*.365, h*.10, h*.062     # ancho de pagina, alzada, canto

    # halo que sube del lomo, como si la pagina emitiera luz
    c = capa(); d = ImageDraw.Draw(c)
    d.polygon([(cx-AN*.5, cy-AL), (cx+AN*.5, cy-AL),
               (cx+AN*1.35, cy-h*.32), (cx-AN*1.35, cy-h*.32)], fill=ORO_VIVO+(26,))
    im = fundir(im, c, w*.055)

    # cuerpo del libro: dos bloques de hojas apilados
    c = capa(); d = ImageDraw.Draw(c)
    for k in range(7):                          # de la hoja de abajo a la de arriba
        t = k/6
        des = CANTO*(1-t)                       # desplazamiento del apilado
        a_ = int(70 + 165*t)
        g = max(1, int(w*.0032))
        for signo in (-1, 1):
            lomo_s = (cx, cy - AL*t*.25 + des)
            ext_s  = (cx + signo*AN, cy - AL + des)
            d.line([lomo_s, ext_s], fill=ORO+(a_,), width=g)
            if k == 6:                          # canto exterior de la hoja superior
                d.line([ext_s, (cx + signo*AN, cy - AL + des + CANTO)],
                       fill=ORO+(int(a_*.7),), width=g)
    # lomo, el eje del libro
    d.line([(cx, cy - AL*.25), (cx, cy + CANTO*1.15)],
           fill=ORO_VIVO+(240,), width=int(w*.0052))
    im = fundir(im, c)

    # renglones insinuados sobre las dos paginas
    c = capa(); d = ImageDraw.Draw(c)
    for signo in (-1, 1):
        for j in range(5):
            u = .30 + j*.13
            x1 = cx + signo*AN*.13
            x2 = cx + signo*AN*.86
            y  = cy - AL*u*.55 + CANTO*.30 + h*.012*j
            d.line([(x1, y), (x2, y)], fill=ORO+(72,), width=int(w*.0016))
    im = fundir(im, c)

    # rayos finos que ascienden desde el lomo
    c = capa(); d = ImageDraw.Draw(c)
    for i in range(13):
        ang = math.radians(-90 + (i-6)*4.6)
        d.line([(cx, cy - AL*.4),
                (cx + math.cos(ang)*h*.30, cy - AL*.4 + math.sin(ang)*h*.30)],
               fill=ORO_VIVO+(40,), width=int(w*.003))
    return acabar(fundir(im, c, w*.012), 'recursos', dest)


# ── 06 · VISÍTANOS — la puerta abierta ────────────────────────────
def visitanos(dest):
    im = tierra((12, 11, 10), (36, 28, 18), (150, 112, 54), w*.5, h*.56, w*.72, 1.7)
    cx = w*.5
    dintel, suelo = h*.30, h*.86
    ancho = w*.20
    # vano iluminado
    c = capa(); d = ImageDraw.Draw(c)
    d.pieslice([cx-ancho, dintel-ancho, cx+ancho, dintel+ancho], 180, 360,
               fill=ORO_VIVO+(58,))
    d.rectangle([cx-ancho, dintel, cx+ancho, suelo], fill=ORO_VIVO+(58,))
    im = fundir(im, c, w*.02)
    # marcos concéntricos de la portada
    c = capa(); d = ImageDraw.Draw(c)
    for k in range(5):
        m = ancho + w*.038*k
        a = int(225*(1-k/5.6))
        g = max(1, int(w*.0048*(1-k/9)))
        d.arc([cx-m, dintel-m, cx+m, dintel+m], 180, 360, fill=ORO+(a,), width=g)
        d.line([(cx-m, dintel), (cx-m, suelo)], fill=ORO+(a,), width=g)
        d.line([(cx+m, dintel), (cx+m, suelo)], fill=ORO+(a,), width=g)
    d.line([(0, suelo), (w, suelo)], fill=ORO+(105,), width=int(w*.0022))
    im = fundir(im, c)
    # umbral: la luz cae hacia el visitante
    c = capa(); d = ImageDraw.Draw(c)
    d.polygon([(cx-ancho, suelo), (cx+ancho, suelo),
               (cx+ancho*2.5, h), (cx-ancho*2.5, h)], fill=ORO_VIVO+(42,))
    return acabar(fundir(im, c, w*.022), 'visitanos', dest)


if __name__ == '__main__':
    dest = sys.argv[1]
    os.makedirs(dest, exist_ok=True)
    print('Generando portadas:')
    for f in (servicios, historia, departamentos, envivo, recursos, visitanos):
        f(dest)
    print('listo')
