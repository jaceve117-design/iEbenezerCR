# Bitácora — iEbenezer CR

Registro de trabajo sobre el monorepo. Cada entrada: fecha, alcance y qué cambió.

---

## 2026-09-12 · La web en vivo estaba serviendo otro repo — despliegue directo (tibas)

**Reporte:** los push a GitHub no se reflejaban en `iebenezer-tibas.pages.dev`.

**Causa raíz (verificada byte a byte):** el proyecto de Cloudflare Pages `iebenezer-tibas` es de
**subida directa** (sin integración Git — confirmado con `wrangler pages project list`), y el
contenido que servía era idéntico al `site/index.html` del monorepo viejo de Altrium
(`Proyectos-Web-ALTRIUM`). Es decir: nadie subió nunca la versión del repo `iEbenezerCR`;
todo lo publicado por git desde el inicio (intro incluido) nunca salió a producción.

**Solución aplicada:** despliegue directo con Wrangler, autenticado en esta máquina:

```
npx wrangler pages deploy tibas/public --project-name=iebenezer-tibas --branch=main
```

**Validación en producción:** el dominio sirve ya el commit `6acfbcd` (marcadores verificados:
anillo del tema, `translateZ(0)` del hero, logo 48 px, GSAP 3.12.5 con SRI, footer compacto,
reset de tap-highlight, sin texto de marca). Prueba de humo headless contra el live: tema claro,
12 tarjetas, GSAP activo, intro retirado, cero errores de consola.

**Pendiente para el dueño del proyecto Cloudflare:** si se quiere publicar por git (que cada
`push` despliegue solo), conectar el proyecto al repo `jaceve117-design/iEbenezerCR` con
**Root directory = `tibas`** y **Build output = `public`** (como documenta el README). Mientras
siga siendo subida directa, el comando de Wrangler de arriba es la vía de publicación.

---

## 2026-09-12 · Ajustes de detalle tras prueba en teléfono (tibas)

**Reporte:** línea que titila al abrir secciones, espacios muertos, onda del tema, texto de la marca, footer lejos del borde, iconos sociales descentrados y desproporcionados, destello de toque en Android.

**1 · La línea que titila — diagnosticada y eliminada.** Reproducida frame a frame con Chrome headless: es una costura de composición. La foto del hero tenía `will-change:transform` permanente, GSAP la escala mientras el panel sube con su propio transform, y capas y recorte se rasterizan por separado → filete oscuro de 1 px en el borde inferior del hero, sólo durante la animación. Fix: `translateZ(0)` en `.view-hero` (capa atómica: recorte y contenido se pintan juntos) y fuera el `will-change` permanente de `#vimg` y de las fotos de Historia. Verificado: frames a 300/600/1000 ms limpios.

**2 · Secciones compactadas.** Hero de 38vh→32vh en escritorio y de 300px→225px en móvil; panel más cerca del header (móvil top 104→78px); márgenes de `.hd`, `.chap`, `.svc`, `.vnav`, `.vfoot`, `.addr` y `.view-body` recortados. En 1440×900 ahora se ven tres servicios al abrir; antes, uno y medio.

**3 · Cambio de tema con dos ondas desde el ícono.** Onda 1: disco/revelado (View Transitions o fallback). Onda 2 nueva: `.anillo`, un aro del color de acento que arranca 90 ms detrás y se desvanece a mitad de camino. Detalle: la primera versión no asignaba `opacity:0` desde JS, la transición de opacidad nunca corría y el anillo quedaba como una banda dorada hasta eliminarse — capturas lo mostraron; corregido y re-verificado (sin residuo a los 8 s).

**4 · Frase de la marca eliminada.** Se quitó «Ministerios Ebenezer / Costa Rica» del header; el nombre vive en el logo y en el `aria-label` del enlace.

**5 · Header reorganizado en tres zonas flex.** Marca / redes / controles: los iconos de Facebook y YouTube quedan centrados de verdad (verificado: centro social 720 = centro pantalla 720), y a la escala de los iconos de tema (SVG 16 px = 16 px; 14 = 14 en móvil).

**6 · Logo más grande.** 38→48 px escritorio, 32→40 px móvil.

**7 · Footer pegado a los bordes.** Padding horizontal del `.hud` de --pad (20-44 px) a 12-24 px.

**8 · Sin tap-highlight.** `-webkit-tap-highlight-color:transparent` en el reset universal (antes sólo cubría `a` y `button`; las tarjetas y fichas destellaban en Android).

Validación: Chrome headless + CDP, escritorio y móvil, consola limpia; deep-link `#servicios` abre panel; botón atrás cierra; tema oscuro/claro ida y vuelta sin residuos.

---

## 2026-09-12 · Refino del sistema de transiciones y animaciones (tibas)

**Meta:** que todo se vea fluido y elegante, sin tirones ni lags al abrir ninguna parte de la web.

### Auditoría (lo que se encontró)

1. El loop del carrusel corría a 60 fps para siempre, incluso quieto y con el panel abierto: escribía transform, opacidad, zIndex, pointerEvents y el gris de las 12 tarjetas en cada frame, y robaba hilo justo al abrir una sección.
2. El grayscale variable (`--g`) se escribía como float en cada frame → repintado de 12 imágenes filtradas por frame durante el arrastre.
3. La sección se construía (`innerHTML` + wiring + 24 miniaturas en En Vivo) en el mismo tick que arrancaba la subida del panel → hitch al abrir.
4. El hero cambiaba `src` en frío, sin decodificar → pop-in a mitad de la animación.
5. Velos con `backdrop-filter` animado por opacidad (drawer 14 px) → re-muestreo del blur en cada frame.
6. Guards de respaldo desalineados con la duración real de las líneas de tiempo.
7. GSAP flotante (`@3`, sin SRI) y entrada del marco colgada del intro aunque el logo fallara.
8. `:hover` pegajoso en táctil; `prefers-reduced-motion` incompleto; botón atrás muerto; rueda bloqueando el pinch del trackpad; cursor repintando en cada tick; 12 tarjetas en móvil pudiendo ser 6.

### Cambios aplicados (`tibas/public/index.html`)

**Carrusel**
- El loop ahora duerme: `despertar()` lo reanuda desde rueda, arrastre, dots, teclado, resize y cierre del panel; con el panel abierto queda apagado y al cerrar asienta la banda por sí solo.
- Escrituras con caché por tarjeta (transform, opacidad, zIndex, pointerEvents) y gris cuantizado en 12 pasos: sólo se toca lo que cambió.
- `will-change` sólo mientras se mueve (clase `.mov` en el deck), no permanente.
- `REP` baja a 1 en pantallas < 900 px: 6 tarjetas en móvil en vez de 12.
- Sin empuje en Z ni inercia cuando `prefers-reduced-motion`.

**Apertura de secciones**
- El cuerpo se monta un frame después de arrancar el deslizamiento (`montarCuerpo`), no en el mismo tick.
- Guard del abierto alineado a 2,6 s (la línea dura ~2,2 s; antes cortaba a 1,5 s).
- Easing de apertura/cierre unificado con los tokens (`EZ.expo/exp entra/sale`), mismo tacto en CSS y GSAP.
- Reduced-motion: apertura/cierre y drawer se asientan directo, sin tween.

**Historial**
- `openSection` empuja entrada propia (`pushState`); el botón atrás y el gesto del sistema cierran el panel (`popstate` → `cerrarVisual(true)`). Cierre dividido en `cerrarVisual()`/`closeView()`.

**Portadas**
- Las 6 portadas de sección se precargan en `load` y el hero lleva `decoding="async"`: sin pop-in.

**Velos**
- `#vscrim` sin `backdrop-filter` (2 px no se veía y costaba un filtro animado); el del drawer baja a 8 px en móvil y su fade se acorta a 0,3 s. Guard del drawer a 1,4/1,1 s según dirección.

**Marco (header + pie)**
- Entrada ligada al intro pero con red propia: si el logo tarda o falla, el marco entra igual (`entrarMarco`/`programarMarco`) en vez de esperar 2 s sobre una web ya visible.

**CSS**
- Todos los `:hover` consolidados en `@media(hover:hover) and (pointer:fine)`: nada de estados pegajosos al tocar.
- `prefers-reduced-motion` completo: matan duraciones y también `transition-delay`.
- `will-change` de `.card` retirado del estado base.

**Varios**
- GSAP clavado a `3.12.5` con `integrity` SRI (hash verificado contra el CDN).
- La rueda ya no secuestra el pinch-zoom del trackpad (`e.ctrlKey` pasa).
- Cursor con gate: si el mouse no se mueve, no escribe nada.
- `.rv` de portadas de ediciones sin doble revelado.

### Validación (Chrome headless + CDP, consola limpia)

- Escritorio 1440×900: intro se retira, marco entra, 12 tarjetas, abrir «Servicios» deja hash `#servicios` + `history.state={eb}`, panel en reposo, **el botón atrás cierra**, el ✕ cierra, tema oscuro aplica.
- Móvil 390×844: 6 tarjetas, panel abre con 9 bloques, «En Vivo» monta 24 ítems de feed y su reproductor con fallback.
- Cero errores y cero avisos en consola en ambos escenarios.

### Pendiente (fuera de alcance de este refino)

- Conectar las descargas de Rhema con el repositorio oficial y los enlaces de App Store / Google Play.
- Confirmar cantones y horarios de las sedes del resto del país.
- Si algún día se pisan los guards del drawer (hoy comparten `guardFicha`), separarlos.
