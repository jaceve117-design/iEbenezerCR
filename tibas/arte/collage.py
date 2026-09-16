# -*- coding: utf-8 -*-
"""
Collage de sección para Ministerios Ebenezer C.R.

Todas las fotos de la carpeta, repartidas sin simetría, con los bordes
difuminados para que no se vea ninguna línea entre ellas. Sin texto.

El encuadre no es aleatorio: cada foto se analiza y el recorte busca
dejar a la gente en el núcleo de su hueco, lejos del borde difuminado.
Así se evitan las caras cortadas a medias y las zonas desenfocadas o
vacías que rompían el ritmo.
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os, sys, glob, random

W, H = 1400, 2000
LOGO_COMUN = '472355186_1028522679306838_1014558922935605396_n.jpg'

# Capturas de pantalla de texto: entran como un muro de letra pequeña y
# rompen el ritmo del collage.
DESCARTES = {'Pueblo 6.jpg'}

# Foto que debe quedar en el centro de la sección, por peso propio.
DESTACADAS = {
    '02. HISTORIA':  '776640720_18366709126242516_2092305493713774485_n.jpg',
    '06. VISÍTANOS': '639752410_18340174399242516_5657618422486155499_n.jpg',   # Pastor General
}

# Fotos que deben caer en la mitad inferior del lienzo.
ABAJO = {
    '06. VISÍTANOS': {'7.jpg'},
}


# ── reparto irregular del lienzo ──────────────────────────────────
def particion(rect, n, rnd):
    """Divide el rectángulo en n piezas de tamaños variados. Cada corte
       elige eje y proporción al azar: nada queda alineado con nada."""
    if n <= 1:
        return [rect]
    x, y, w, h = rect
    horizontal = (w < h) if rnd.random() < 0.78 else (w >= h)
    izq = max(1, int(round(n * rnd.uniform(0.36, 0.64))))
    der = n - izq
    if der < 1:
        izq, der = n - 1, 1
    corte = min(0.78, max(0.22, izq / n + rnd.uniform(-0.10, 0.10)))
    if horizontal:
        hh = int(h * corte)
        a, b = (x, y, w, hh), (x, y + hh, w, h - hh)
    else:
        ww = int(w * corte)
        a, b = (x, y, ww, h), (x + ww, y, w - ww, h)
    return particion(a, izq, rnd) + particion(b, der, rnd)


# ── dónde está lo que importa de cada foto ────────────────────────
def _suavizar(a, radio):
    """Difuminado sobre un array float. PIL no acepta el modo 'F', así que
       se normaliza a 8 bits, se difumina y se vuelve a 0..1."""
    m = float(a.max())
    if m <= 1e-6:
        return a
    u8 = Image.fromarray(np.clip(a / m * 255.0, 0, 255).astype(np.uint8), 'L')
    return np.asarray(u8.filter(ImageFilter.GaussianBlur(radio))).astype(np.float32) / 255.0


def mapa_interes(im):
    """Mapa pequeño con el 'peso' de cada zona de la foto.

       Dos señales que se suman:
       · detalle — magnitud del gradiente. Una cara tiene estructura; una
                   pared lisa o un hombro desenfocado, no. Es lo que aparta
                   el recorte de las zonas muertas.
       · piel    — tono de piel en YCbCr. Señala dónde hay gente, aunque con
                   la luz de colores del escenario no sea fiable por sí
                   sola; por eso pesa menos que el detalle.
    """
    ch = 180
    chico = im.convert('RGB').resize(
        (ch, max(1, round(ch * im.height / im.width))), Image.BILINEAR)
    a = np.asarray(chico).astype(np.float32)

    gris = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    gy, gx = np.gradient(gris)
    # un desenfoque agrupa el detalle en regiones, no en bordes sueltos
    detalle = _suavizar(np.hypot(gx, gy), 3.2)

    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    piel = _suavizar(
        ((cr > 133) & (cr < 180) & (cb > 77) & (cb < 130)).astype(np.float32), 4.5)

    return 0.72 * detalle + 0.28 * piel


def recorte_bueno(im, w, h, interes):
    """Encuadre que deja lo importante en el núcleo del hueco.

       Puntúa cada posición candidata: suma el interés del núcleo y resta,
       con más peso, el de la banda del borde. Esa resta es la clave — es lo
       que impide que una cara quede justo donde la máscara la desvanece.
    """
    w, h = max(1, int(w)), max(1, int(h))
    r_dest, r_orig = w / h, im.width / im.height
    if r_orig > r_dest:
        nh, nw = h, int(round(h * r_orig))
    else:
        nw, nh = w, int(round(w / r_orig))
    nw, nh = max(nw, w), max(nh, h)

    libre_x, libre_y = nw - w, nh - h
    grande = im.resize((nw, nh), Image.LANCZOS)
    if libre_x < 2 and libre_y < 2:
        return grande.crop((0, 0, w, h))

    mh, mw = interes.shape
    vw, vh = mw * w / nw, mh * h / nh
    borde = max(1, int(min(vw, vh) * 0.16))       # la banda que se difumina

    mejor, mejor_p = (0, 0), -1e18
    PASOS = 13
    for i in range(PASOS):
        for j in range(PASOS):
            ox = libre_x * i / (PASOS - 1) if libre_x else 0
            oy = libre_y * j / (PASOS - 1) if libre_y else 0
            mx, my = int(mw * ox / nw), int(mh * oy / nh)
            x2, y2 = int(mx + vw), int(my + vh)
            if x2 > mw or y2 > mh:
                continue
            ventana = interes[my:y2, mx:x2]
            if ventana.size == 0:
                continue
            if ventana.shape[0] > 2 * borde and ventana.shape[1] > 2 * borde:
                nucleo = ventana[borde:-borde, borde:-borde]
            else:
                nucleo = ventana
            p = nucleo.sum() - 1.35 * (ventana.sum() - nucleo.sum())
            # a igualdad, encuadre algo alto: las caras viven en el tercio
            # superior, no en el centro geométrico
            if libre_y:
                p -= abs(oy / libre_y - 0.38) * ventana.sum() * 0.12
            if p > mejor_p:
                mejor_p, mejor = p, (int(ox), int(oy))

    dx, dy = mejor
    return grande.crop((dx, dy, dx + w, dy + h))


def mascara_suave(w, h, difuminado):
    """Máscara con los bordes desvanecidos, para que las piezas se fundan."""
    m = Image.new('L', (w, h), 0)
    b = int(difuminado * 1.15)
    ImageDraw.Draw(m).rectangle([b, b, w - b, h - b], fill=255)
    return m.filter(ImageFilter.GaussianBlur(difuminado))


# ── collage ───────────────────────────────────────────────────────
def collage(carpeta, salida, semilla=7):
    rnd = random.Random(semilla)
    nombre_carpeta = os.path.basename(carpeta)
    rutas = sorted(glob.glob(os.path.join(carpeta, '*.jpg')) +
                   glob.glob(os.path.join(carpeta, '*.png')))
    fotos = [p for p in rutas
             if os.path.basename(p) != LOGO_COMUN
             and os.path.basename(p) not in DESCARTES]
    if not fotos:
        raise SystemExit('sin fotos en ' + carpeta)
    rnd.shuffle(fotos)

    destacada = DESTACADAS.get(nombre_carpeta)
    ruta_dest = next((p for p in fotos if os.path.basename(p) == destacada), None)
    if ruta_dest:
        fotos.remove(ruta_dest)
        fotos.insert(0, ruta_dest)
    print(f'  {nombre_carpeta}: {len(fotos)} fotos'
          + (f'  ·  destacada al centro' if ruta_dest else ''))

    piezas = particion((0, 0, W, H), len(fotos), rnd)

    # El hueco de la destacada: grande y cerca del centro. La medida premia
    # área y penaliza distancia, así no acaba en una esquina ni en un resto.
    if ruta_dest:
        cx, cy = W / 2, H / 2
        def mide(p):
            x, y, w, h = p
            d = float(np.hypot(x + w / 2 - cx, y + h / 2 - cy))
            return (w * h) / (1 + d * 1.6)
        i_centro = max(range(len(piezas)), key=lambda i: mide(piezas[i]))
        piezas[0], piezas[i_centro] = piezas[i_centro], piezas[0]

    # Las que van abajo: se intercambian con la pieza más baja disponible.
    for nombre in ABAJO.get(nombre_carpeta, ()):
        k = next((j for j, f in enumerate(fotos)
                  if os.path.basename(f) == nombre and j != 0), None)
        if k is None:
            continue
        libres = [j for j in range(len(piezas)) if j not in (0, k)]
        if not libres:
            continue
        j_bajo = max(libres, key=lambda j: piezas[j][1] + piezas[j][3] / 2)
        if piezas[j_bajo][1] > piezas[k][1]:
            piezas[k], piezas[j_bajo] = piezas[j_bajo], piezas[k]

    lienzo = Image.new('RGBA', (W, H), (18, 18, 20, 255))
    orden = sorted(range(len(piezas)), key=lambda i: -piezas[i][2] * piezas[i][3])

    for i in orden:
        x, y, w, h = piezas[i]
        margen = int(min(w, h) * 0.16) + 10          # solapan para fundirse
        X, Y = x - margen, y - margen
        Wp, Hp = w + margen * 2, h + margen * 2
        try:
            foto = Image.open(fotos[i]).convert('RGB')
        except Exception as e:
            print('   x', fotos[i], e)
            continue
        trozo = recorte_bueno(foto, Wp, Hp, mapa_interes(foto))
        dif = max(9, int(min(Wp, Hp) * 0.11))
        trozo.putalpha(mascara_suave(Wp, Hp, dif))
        lienzo.alpha_composite(trozo.convert('RGBA'), (X, Y))

    # oscurece los extremos para que el conjunto se asiente
    vin = Image.new('L', (W, H), 0)
    ImageDraw.Draw(vin).ellipse([-W * 0.28, -H * 0.14, W * 1.28, H * 1.14], fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(W * 0.10))
    base = lienzo.convert('RGB')
    im = Image.composite(base, Image.blend(base, Image.new('RGB', (W, H)), 0.42), vin)

    im.save(salida, 'WEBP', quality=80, method=6)
    print(f'  -> {os.path.basename(salida)}  {os.path.getsize(salida)//1024} KB')
    return im


if __name__ == '__main__':
    base, carpeta, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    semilla = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    collage(os.path.join(base, carpeta), salida, semilla)
