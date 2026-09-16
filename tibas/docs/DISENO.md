# Cómo está hecha la web — Ebenezer Tibás

Notas técnicas del sitio: de dónde sale el movimiento del inicio, cómo están
medidas las físicas y por qué cada decisión es la que es. Para el qué y el
cuándo del proyecto está `BP.md`, en la raíz de la carpeta del proyecto; para el
diario de cambios, `../../BITACORA.md`.

El sitio entero es `../public/index.html` — autocontenido, sin build.

Para servirlo en local:

```bash
python -m http.server 5199 --directory "1. WEB/tibas/public"
```

También está en `.claude/launch.json` con el nombre `ebenezer`.

Los dos prototipos de los que salió la estética actual están fuera del
repositorio, en `2. MATERIAL/referencias/propuestas-iniciales/`.

---

## El home — réplica del ejemplo pmndrs

El inicio replica `pmndrs.github.io/examples/infinite-scroll`, reconstruido en DOM
(CSS 3D + un loop `requestAnimationFrame`) en vez de WebGL. Decompilé el bundle original
para sacar los parámetros exactos:

| Parámetro | Original (R3F) | Aquí |
|---|---|---|
| Tarjetas por pantalla | 3, centros cada `viewport/3` | igual (`STEP = VW/3`) |
| Ancho de tarjeta | `viewport/3 − margen` | igual |
| Profundidades Z | `-1 · 0 · +1` repitiendo | `-560 · -90 · +170 px`, `perspective:1200` |
| Escalas resultantes | ~0.68 / 0.83 / 1.0 medidas en la referencia | 0.68 / 0.93 / 1.17 |
| Ciclo completo | 4 pantallas, 4 palabras gigantes | igual |
| Pantallas angostas | paso `1.5/3` en vez de `1/3` | `VW/1.9`, con la profundidad comprimida |

**Del original se conserva:** el empuje en Z con la velocidad del scroll — mientras te
movés, todas las tarjetas se adelantan hacia el espectador y retroceden al frenar
(`position.z = damp(max(0, delta*50))` en el código original).

**Blanco y negro / color:** en vez del color por velocidad del original, la tarjeta que
queda **en el centro de la pantalla va a color** y el resto en blanco y negro, con
transición continua a medida que pasan. El cálculo tiene en cuenta la escala en
perspectiva de cada tarjeta, así el punto de color cae exactamente en el centro visual.
Al pasar el mouse por cualquier tarjeta también se enciende, como señal de que es clicable.

### Cómo se recorre — la física

**No hay imán.** La banda nunca se ancla a una tarjeta ni la deja «centrada» a la fuerza:
queda donde la soltás. La sensación sale de tres constantes, arriba del loop en el código:

| Constante | Valor | Qué hace |
|---|---|---|
| `AMORT` | 0.075 | Cuánto se retrasa la banda respecto al dedo. Bajo = pesado. **Ese retraso es lo gomoso**: agarrás y la masa tarda en obedecer. |
| `ARRASTRE` | 1.12 | Píxeles que camina el contenido por cada píxel de dedo. Cerca de 1 se siente conectado. |
| `FRENO` | 0.945 | Cuánto conserva la inercia al soltar. Alto = deslizamiento largo que se apaga solo. |

Todo va corregido por delta de tiempo, así se siente **igual a 60 y a 120 Hz** en vez de
ir al doble de rápido en pantallas rápidas.

Un impulso fuerte recorre unos 1.600 px (≈ 8 tarjetas) en 2,5 s, con la velocidad
subiendo los primeros 20 frames antes de decaer — la banda «alcanza» al gesto y luego
se deja ir. La rueda del ratón deja bastante menos inercia que el dedo (el factor 0.55
impide que un trackpad la acumule sin freno).

Como no hay imán, la banda puede quedar entre dos tarjetas. Por eso **el color se mide
contra la tarjeta más cercana, no contra el centro absoluto**: siempre hay una a color
en vez de quedar todo gris, y en el punto medio exacto las dos se cruzan.

| Entrada | Comportamiento |
|---|---|
| Rueda del ratón (vertical **u** horizontal) | Ambos ejes empujan el mismo recorrido |
| Arrastrar (ratón, dedo o lápiz) | Pointer Events unificado, con inercia al soltar |
| Flechas ← → | Un paso exacto |
| Enter / Espacio | Abre la sección enfocada |
| Puntos del pie | Salto a esa sección por el camino más corto |
| Tocar una tarjeta | La abre |

> **Bug corregido — en móvil no abría ninguna tarjeta.** La tolerancia para distinguir
> toque de arrastre era de 8 px. Un ratón se mueve 0–2 px en un clic, pero **un dedo
> rueda entre 5 y 15 px en un toque normal**, así que casi todos los toques se contaban
> como arrastre. Ahora hay dos tolerancias: 6 px para ratón, 15 px para dedo y lápiz.
> Además, mientras el gesto no supera la tolerancia no se mueve nada — un toque no
> empuja la banda ni un píxel — y al cruzarla se re-ancla el origen para que el arrastre
> no dé un salto.

**Al pulsar cualquier tarjeta** sube desde abajo un panel con la información de esa
sección — *push-up*, `expo.out` en 1 s. El panel **no cubre toda la pantalla**: deja ver
el home por arriba y a los lados (en móvil, sólo por arriba). Detrás se enciende un velo
translúcido, y el home retrocede a escala 0.955 con opacidad 0.5, así se lee como una
capa encima y no como un cambio de página.

**Se cierra de cinco maneras**, todas con el mismo *push-down*: tocando **fuera del
panel** (el velo), el botón ✕, la tecla `Esc`, el logo del header, o deslizando hacia
abajo en móvil (cuando el contenido ya está arriba del todo).

Dentro, la sección usa la estética **Aurora**: blobs de color de fondo, tipografía
Garamond, cursor magnético, fichas laterales.

> **Bug corregido — el clic no llegaba a la tarjeta.** La causa era
> `setPointerCapture()`: al empezar un arrastre capturábamos el puntero en el escenario,
> y el navegador entonces **reasigna el evento `click` al elemento que capturó**. Ahora
> la captura se toma sólo cuando el gesto ya es un arrastre de verdad, y el toque se
> resuelve en `pointerup` con `elementFromPoint`.

> **Bug corregido — la tarjeta se abría y se retraía sola (táctil).** El culpable era
> el *ghost click*: tras un toque el navegador dispara, además del `pointerup`, un
> `click` de compatibilidad que **no conserva el objetivo original** — se re-impacta
> contra lo que haya en esas coordenadas en ese instante. Como el toque abría el panel
> y con él aparecía el velo, el click fantasma caía sobre el velo y lo cerraba en el
> mismo gesto. De ahí que unas veces se retrajera de inmediato, otras se quedara a medio
> camino (las dos animaciones pisándose) y otras pareciera necesitar varios intentos.
>
> Resuelto por triplicado: el velo cierra con `pointerdown` (un click fantasma no genera
> pointerdown, así que es inmune por construcción), hay una ventana de gracia de 380 ms
> tras la apertura en la que nada puede cerrar el panel, y el click sobre el velo se
> traga para que no haga nada más.

> **Robustez del contenido.** El revelado de los bloques dentro del panel pasó de
> tweens de GSAP a **transiciones CSS** con una clase `.in`, y ya no cuelga del timeline.
> Antes, si el navegador estrangulaba `requestAnimationFrame` (pestaña de fondo, ahorro
> de energía, equipo cargado), el panel podía abrirse **en blanco**. Los primeros diez
> bloques entran por orden y del resto se encarga un `IntersectionObserver`, que no
> depende de rAF.

**Proporciones.** Todo el header comparte una misma altura (`--ctl`: 38 px en
escritorio, 32 px en móvil) — iconos sociales, botón de tema, píldora de En vivo y logo —
y el texto se dimensiona contra ella. En móvil la píldora pasa a ser un botón cuadrado
igual que el del tema. El pie baja a 7,5 px con los puntos en su propia línea: antes
ocupaba tres líneas y se comía la pantalla del teléfono.

**El panel scrollea completo.** `.view-body` lleva `touch-action:pan-y` y
`overscroll-behavior:contain`, y la portada ocupa 38 vh en escritorio y 34 vh en móvil
(antes 44 vh, que dejaba muy poco cuerpo visible). El gesto de cerrar deslizando hacia
abajo exige 140 px y sólo arranca con el contenido ya arriba del todo, para no estorbar
al scroll normal.

**Temas:** claro = el gris `#EFEFEF` del ejemplo original (por defecto).
Oscuro = Aurora, `#08080A`. La aurora de fondo solo aparece dentro de las secciones;
el home se mantiene limpio como la referencia.

## Header y footer

**Header** — izquierda: «Ministerios Ebenezer / Costa Rica». Centro: Facebook y YouTube.
Derecha: cambio de tema → botón En vivo → logo del águila.
El logo va **incrustado como data URI** (PNG de 440 px reducido a 64 colores, 18 KB), así
el archivo funciona con doble clic sin depender de rutas relativas.

**Footer** — izquierda: «Todos los derechos reservados · Ministerios Ebenezer Costa Rica
2026». Centro: indicador de tarjetas. Derecha: «Designed by Altriumcr.com».
En móvil se apila: puntos arriba, los dos textos abajo en una sola línea.

La navegación es el carrusel: no hay menú de texto. Los puntos saltan a cualquier sección
y dentro de cada panel hay anterior/siguiente al pie.

## Tipografía

Una sola familia: **EB Garamond** — revival de los tipos de Claude Garamont (s. XVI),
el linaje de la imprenta litúrgica. Toda la jerarquía se construye con **variantes
internas**, nunca mezclando familias:

| Uso | Variante |
|---|---|
| Titulares de panel, dirección | 500, `-0.025em`, caja normal |
| Subtítulos de sección (`h2`) | 500 |
| Encabezados de bloque (`h3`) | 600 |
| Cuerpo de texto | 400, 17–19 px, interlínea 1.68 |
| Entradillas y citas | 400 **itálica** |
| Versalitas (`.mono`, `.k`, días) | 500, caja alta, `+0.20em` de interletrado |
| Horas, años y cifras | 500 con `lining-nums tabular-nums` |

Garamond tiene la altura de x baja, así que el cuerpo va en 17–19 px (no 15–16) y con
más interlínea de lo habitual. Los titulares van en caja normal, no en mayúsculas: en
una romana clásica la caja alta grande se lee dura. Las mayúsculas quedan sólo para las
etiquetas pequeñas, muy espaciadas — que es donde una serif las hace ver elegantes.

> **Bug corregido de paso:** el `font-size` del `body` era
> `clamp(17px,.5vw+15.2px,19px)`. En CSS la suma dentro de `clamp()` necesita espacios
> alrededor del `+`; sin ellos toda la declaración se descarta en silencio y el cuerpo
> caía a los 16 px por defecto del navegador. Estaba así desde el primer prototipo.

## Secciones

1. **Servicios** — los cuatro horarios de la semana:
   Domingo 10:00 a.m. (General) · Lunes 7:00 p.m. (Oración) ·
   Viernes 7:00 p.m. (Familiar) · Sábado 2:30 p.m. (Jóvenes).
   Debajo, seis notas de «qué esperar» para quien viene por primera vez.
2. **Historia** — cinco capítulos de 2005 a 2026, con parallax en las fotos, más tres
   cifras: 21 años de obra · 20+ iglesias en el territorio nacional · 1 casa central.
3. **Departamentos** — los seis ministerios: Alabanza, Niños, Doulos (diaconado),
   Pastoral, Jóvenes y Audiovisual. Cada uno abre una ficha lateral con su agenda.
4. **En Vivo** — reproductor de YouTube con estado de transmisión + pestañas
   YouTube / Facebook.
5. **Recursos** — Revista Rhema (rejilla de ediciones con selector de idioma),
   Aplicaciones y Videoteca. Los tres abren ficha lateral.
6. **Visítanos** — la dirección: **Tibás, San José, Costa Rica**, tratada como pieza
   tipográfica a gran tamaño, con enlace a Google Maps. Debajo, las congregaciones del
   resto del país: Alajuela, Cartago, Limón, Heredia, Puntarenas y Guanacaste.

Navegación anterior/siguiente al pie de cada panel, y deep-links (`index.html#historia`).

## En Vivo — los dos modos

**Modo actual (sin API, funciona ya):**
carga `youtube.com/embed/live_stream?channel=…`. Si hay señal, entra sola.
A los 4 s sin señal detectada cae a la playlist de subidas `UU…` (el servicio más reciente).

**Modo real (recomendado):** desplegá `worker/live.js` en Cloudflare Workers y pegá
la URL en `CFG.liveEndpoint` dentro de `index.html`. Con eso el sitio obtiene:

- badge **EN VIVO** real en el nav (se repinta cada 90 s)
- título de la transmisión en curso
- el último video real del canal, siempre fresco

El Worker guarda la API key como secreto (nunca viaja al navegador) y cachea 60 s en el
borde: ~1.440 unidades de cuota al día sin importar el tráfico, contra las 10.000 gratis.
Las instrucciones de deploy están en la cabecera del propio archivo.

Si el Worker está caído o no configurado, el front cae solo al modo sin API. Nunca rompe.

---

## Facebook

Page Plugin oficial en iframe (sin API key). Muestra el timeline público de
`facebook.com/MinisteriosEbenezerCR`. Un feed nativo dentro del diseño requeriría un
token de página de Graph API — se puede añadir al mismo Worker si lo querés.

---

## Detalles técnicos

- HTML + CSS + JS puro. Única dependencia: **GSAP 3** por CDN.
  Si el CDN falla, un shim hace que el sitio funcione igual, sin animaciones.
- El carrusel corre en un loop `requestAnimationFrame` propio: solo `transform` y
  `opacity`, sin tocar layout. `ResizeObserver` re-mide y re-centra ante cualquier cambio.
- Tema claro/oscuro con icono, persistido en `localStorage`, con `meta[theme-color]`
  sincronizado para la barra del navegador móvil.
- Cursor magnético solo en escritorio con puntero fino.
- `prefers-reduced-motion` respetado.
- Menú de pantalla completa en móvil con revelado por máscara.

---

## Datos reales ya cableados

- Canal YouTube `UCK6O7BIAhJAaTTSPqnF-o8g` — [@ministeriosebenezerc.r1904](https://www.youtube.com/@ministeriosebenezerc.r1904)
- Página Facebook `MinisteriosEbenezerCR`
- 24 servicios reales del canal (títulos, fechas y miniaturas vía `i.ytimg.com`)

## Pendiente (necesito input tuyo)

- [ ] **Fotografía propia** del templo y la congregación — hoy uso miniaturas de YouTube
- [ ] **Dirección exacta** — hoy dice «Tibás, San José». Falta calle, señas y el enlace
      real de Maps (el actual es una búsqueda por nombre, no una ubicación fijada)
- [ ] **Las otras sedes**: las seis provincias están puestas como referencia, pero los
      cantones y horarios de cada una son inventados. Hay que confirmarlos
- [ ] **Historia**: 2005 y los 21 años están confirmados por vos; los hitos de
      **2011, 2016 y 2021 son una reconstrucción aproximada** — hay que contrastarlos
      con el archivo de la iglesia
- [ ] **Enlaces reales**: descargas de Rhema, y App Store / Google Play de las aplicaciones
- [ ] Confirmar si falta algún ministerio en Departamentos
- [ ] Desplegar el Worker y pegar la URL en `CFG.liveEndpoint`
