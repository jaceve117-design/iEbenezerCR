# -*- coding: utf-8 -*-
"""
Collage de sección para Ministerios Ebenezer C.R.

Todas las fotos de la carpeta, repartidas sin simetría, con los bordes
difuminados para que no se vea ninguna línea entre ellas. En el centro,
el logo dentro de un círculo de color plano con un aro de luz.
Sin texto de ningún tipo.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import os, sys, glob, random, math

W, H = 1400, 2000
LOGO_COMUN = '472355186_1028522679306838_1014558922935605396_n.jpg'

# Capturas de pantalla de texto: entran como un muro de letra pequeña y
# rompen el ritmo del collage.
DESCARTES = {'Pueblo 6.jpg'}


# ── reparto irregular del lienzo ──────────────────────────────────
def particion(rect, n, rnd, prof=0):
    """Divide el rectángulo en n piezas de tamaños variados (BSP con sesgo
       aleatorio). Nada de rejillas: cada corte elige eje y proporción."""
    if n <= 1:
        return [rect]
    x, y, w, h = rect
    # el eje del corte tiende al lado largo, pero no siempre
    horizontal = (w < h) if rnd.random() < 0.78 else (w >= h)
    izq = max(1, int(round(n * rnd.uniform(0.36, 0.64))))
    der = n - izq
    if der < 1:
        izq, der = n - 1, 1
    frac = izq / n
    corte = frac + rnd.uniform(-0.10, 0.10)
    corte = min(0.78, max(0.22, corte))
    if horizontal:
        hh = int(h * corte)
        a = (x, y, w, hh)
        b = (x, y + hh, w, h - hh)
    else:
        ww = int(w * corte)
        a = (x, y, ww, h)
        b = (x + ww, y, w - ww, h)
    return particion(a, izq, rnd, prof + 1) + particion(b, der, rnd, prof + 1)


def cubrir(im, w, h, rnd):
    """Recorta la foto para llenar el hueco, con un encuadre algo variado."""
    w, h = max(1, int(w)), max(1, int(h))
    r_dest, r_orig = w / h, im.width / im.height
    if r_orig > r_dest:
        nh = h; nw = int(round(h * r_orig))
    else:
        nw = w; nh = int(round(w / r_orig))
    im = im.resize((max(nw, w), max(nh, h)), Image.LANCZOS)
    # el encuadre no siempre al centro: da variedad sin desordenar
    dx = int((im.width - w) * rnd.uniform(0.25, 0.75))
    dy = int((im.height - h) * rnd.uniform(0.20, 0.62))
    return im.crop((dx, dy, dx + w, dy + h))


def mascara_suave(w, h, difuminado):
    """Máscara con los bordes desvanecidos, para que las piezas se fundan."""
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    b = int(difuminado * 1.15)
    d.rectangle([b, b, w - b, h - b], fill=255)
    return m.filter(ImageFilter.GaussianBlur(difuminado))


# ── el logo, recortado de su fondo plano ──────────────────────────
def logo_alfa(ruta):
    """La imagen es el logo blanco sobre un color plano. Se despeja el alfa
       midiendo cuánto se acerca cada píxel al blanco desde ese fondo."""
    im = Image.open(ruta).convert('RGB')
    fondo = im.getpixel((6, 6))
    px = im.load()
    out = Image.new('LA', im.size)
    o = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            t = 0.0
            for c, f in ((r, fondo[0]), (g, fondo[1]), (b, fondo[2])):
                den = 255 - f
                if den > 8:
                    t += (c - f) / den
            t = max(0.0, min(1.0, t / 3))
            o[x, y] = (255, int(t * 255))
    return out.convert('RGBA')


def centro_logo(lienzo, logo, color, rnd):
    """Círculo de color plano con el logo dentro y un aro de luz alrededor."""
    R = int(W * 0.165)          # disco discreto, no protagonista
    cx, cy = W // 2, int(H * 0.5)
    SS = 3                                   # sobremuestreo para el borde
    lado = R * 2 * SS

    disco = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(disco)
    d.ellipse([0, 0, lado - 1, lado - 1], fill=color + (255,))

    # el logo dentro, centrado
    lw = int(lado * 0.66)
    lg = logo.resize((lw, int(lw * logo.height / logo.width)), Image.LANCZOS)
    disco.alpha_composite(lg, ((lado - lg.width) // 2, (lado - lg.height) // 2))

    disco = disco.resize((R * 2, R * 2), Image.LANCZOS)

    # sombra suave para despegarlo del collage
    sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    e = R/329.0                                  # todo el aro escala con el disco
    ds.ellipse([cx-R-14*e, cy-R-10*e, cx+R+14*e, cy+R+20*e], fill=(0, 0, 0, 118))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(26*e)))

    lienzo.alpha_composite(disco, (cx - R, cy - R))

    # ── aro de luz ──────────────────────────────────────────────
    # Tres capas: un resplandor ancho que se derrama sobre las fotos, un
    # anillo medio y un filo nítido justo en el borde del disco. Así se
    # lee como luz y no como un simple contorno dibujado.
    for radio_extra, grosor, alfa, desenfoque in (
            (26*e, 30*e, 88,  30*e),   # resplandor exterior
            (11*e, 14*e, 160, 13*e),   # anillo medio
            ( 3*e,  7*e, 215,  5*e)):  # cerca del filo
        capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dc.ellipse([cx-R-radio_extra, cy-R-radio_extra,
                    cx+R+radio_extra, cy+R+radio_extra],
                   outline=(255, 251, 240, alfa), width=max(1, int(grosor)))
        lienzo.alpha_composite(capa.filter(ImageFilter.GaussianBlur(desenfoque)))

    # filo limpio sobre el borde mismo, dibujado al doble y reducido
    filo = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    ImageDraw.Draw(filo).ellipse(
        [(cx - R) * 2, (cy - R) * 2, (cx + R) * 2, (cy + R) * 2],
        outline=(255, 254, 250, 255), width=max(2, int(9*e)))
    lienzo.alpha_composite(filo.resize((W, H), Image.LANCZOS))
    return lienzo


# ── collage ───────────────────────────────────────────────────────
def collage(carpeta, color, salida, semilla=7):
    rnd = random.Random(semilla)
    rutas = sorted(glob.glob(os.path.join(carpeta, '*.jpg')) +
                   glob.glob(os.path.join(carpeta, '*.png')))
    logo_ruta = next((p for p in rutas if os.path.basename(p) == LOGO_COMUN), None)
    fotos = [p for p in rutas
             if p != logo_ruta and os.path.basename(p) not in DESCARTES]
    if not fotos:
        raise SystemExit('sin fotos en ' + carpeta)
    rnd.shuffle(fotos)
    print(f'  {os.path.basename(carpeta)}: {len(fotos)} fotos')

    piezas = particion((0, 0, W, H), len(fotos), rnd)
    lienzo = Image.new('RGBA', (W, H), (18, 18, 20, 255))

    orden = sorted(range(len(piezas)), key=lambda i: -piezas[i][2] * piezas[i][3])
    for k, i in enumerate(orden):
        x, y, w, h = piezas[i]
        margen = int(min(w, h) * 0.16) + 10          # solapan para fundirse
        X, Y = x - margen, y - margen
        Wp, Hp = w + margen * 2, h + margen * 2
        try:
            foto = Image.open(fotos[k]).convert('RGB')
        except Exception as e:
            print('   x', fotos[k], e); continue
        trozo = cubrir(foto, Wp, Hp, rnd)
        dif = max(9, int(min(Wp, Hp) * 0.11))
        trozo.putalpha(mascara_suave(Wp, Hp, dif))
        lienzo.alpha_composite(trozo.convert('RGBA'), (X, Y))

    # unifica un poco el conjunto y oscurece los extremos
    vin = Image.new('L', (W, H), 0)
    ImageDraw.Draw(vin).ellipse([-W * 0.28, -H * 0.14, W * 1.28, H * 1.14], fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(W * 0.10))
    base = lienzo.convert('RGB')
    lienzo = Image.composite(base, Image.blend(base, Image.new('RGB', (W, H)), 0.42),
                             vin).convert('RGBA')

    logo = logo_alfa(logo_ruta) if logo_ruta else None
    if logo:
        lienzo = centro_logo(lienzo, logo, color, rnd)

    im = lienzo.convert('RGB')
    im.save(salida, 'WEBP', quality=86, method=6)
    print(f'  -> {salida}  {os.path.getsize(salida)//1024} KB')
    return im


if __name__ == '__main__':
    base, carpeta, color, salida = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    semilla = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    c = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    collage(os.path.join(base, carpeta), c, salida, semilla)
