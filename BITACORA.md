# Bitácora — iEbenezer CR

Registro de trabajo sobre el monorepo. Cada entrada: fecha, alcance y qué cambió.

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
