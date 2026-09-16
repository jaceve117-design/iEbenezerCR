# Bitácora de progreso

Dónde está el proyecto, qué se ha hecho y qué falta. Para el detalle técnico de
cada cambio —el porqué de cada decisión— está `BITACORA.md`; para cómo está
construido el sitio por dentro, `tibas/docs/DISENO.md`.

**Actualizado:** 15 de septiembre de 2026
**En línea:** https://iebenezer-tibas.pages.dev
**Repositorio:** https://github.com/jaceve117-design/iEbenezerCR

---

## En una frase

El sitio de la iglesia madre en Tibás está en línea y funcionando, con las seis
secciones completas. Falta confirmar unos datos que están puestos como
provisionales y conectar el estado real de transmisión; hasta entonces el sitio
lleva bloqueado el indexado en buscadores.

---

## Estado por partes

| Parte | Estado | Nota |
|---|---|---|
| Inicio — scroll infinito | **Listo** | Ratón, rueda y dedo. Réplica del modelo pmndrs. |
| Servicios | **Listo** | Horarios semanales + servicios especiales. |
| Historia | Funciona, **datos por confirmar** | Tres hitos están inventados. |
| Ministerios | **Listo** | Los seis, sin fotos, sólo nombre y descripción. |
| En Vivo | Funciona, **a medias** | El próximo directo se calcula solo; el indicador de «en vivo» todavía no es real. |
| Recursos | **Listo** | |
| Visítanos | Funciona, **datos por confirmar** | Falta dirección exacta; las sedes del país están inventadas. |
| Temas claro / oscuro | **Listo** | Con la onda que sale del propio icono. |
| Intro de partículas | **Listo** | 3 s, en cada carga. |
| Móvil | **Listo** | Probado a 375 y 412 px de ancho. |
| Apple (iOS / Safari) | **Listo** | Suelo bajado a iOS 15. |
| Despliegue | Funciona, **manual** | Ver «Lo que falta». |

---

## Lo que se ha hecho

### El punto de partida

Se pidió una web elegante y distinta —«no lo mismo de otras webs para
iglesias»— y se presentaron dos propuestas: *Santuario* y *Aurora*. Se eligió
Aurora, pero con una condición que cambió el proyecto entero: que el sistema de
navegación fuese el **scroll infinito de pmndrs**, no un menú. Las secciones son
tarjetas que se recorren con el dedo, la rueda o el ratón, y al tocar una se
abre.

Las dos propuestas se guardan en `material/referencias/propuestas-iniciales/`.

### El inicio

Para clavar el movimiento se decompiló el bundle original de la demo y se sacaron
los parámetros exactos en vez de aproximarlos a ojo: distancias, profundidades,
escalas y el empuje en Z con la velocidad. Está reconstruido en DOM con CSS 3D y
un bucle propio, no en WebGL — pesa una fracción y corre igual. Las medidas y el
razonamiento están en `tibas/docs/DISENO.md`.

Se cambió una cosa respecto al original: en vez de colorear por velocidad, **la
tarjeta que queda en el centro va a color y el resto en blanco y negro**, con
transición continua.

### Las secciones

Se abren de abajo arriba como una hoja, y se cierran arrastrando hacia abajo con
física de iOS: responde al dedo 1:1, resiste hacia arriba y decide por velocidad,
no sólo por distancia. Cada una lleva un versículo en la cabecera.

Esto costó varias vueltas. Las tarjetas primero no abrían —la captura del puntero
retargeteaba el clic—, luego no abrían en móvil —el umbral de 8 px no distingue
un toque de un roce—, luego abrían y se retraían solas —el clic fantasma del
táctil caía sobre el velo recién aparecido—, y al final se sentían partidas en
dos al deslizar, porque la portada estaba clavada y el contenido le pasaba por
detrás. Todo eso está resuelto y contado paso a paso en `BITACORA.md`.

### Las imágenes

No hay stock. Las portadas son **collages generados a partir de las fotos reales**
de la iglesia, una por sección, con reparto irregular y bordes difuminados para
que no se vea ninguna costura. El encuadre no es aleatorio: cada foto se analiza
y el recorte busca dejar a la gente en el centro de su hueco, para que no salgan
caras cortadas. El generador es `tibas/arte/collage.py`; las fotos originales
están en `material/fotos/`.

### La identidad

Una sola familia tipográfica —EB Garamond— con sus variantes, para que todo sea
coherente. Dos temas: *Piedra* (gris perla con hilo dorado) y *Azabache*. El
cambio de tema no es un corte: sale una onda desde el propio icono, medida en el
momento de presionar.

La web abre siempre con el logo formándose en partículas sobre fondo perla, tres
segundos. Si el tema activo es el oscuro, hay una transición desde el perla hasta
el negro en vez de un salto.

### En Vivo

El cuadro del próximo directo **se calcula solo** desde el calendario de
transmisiones (miércoles 19:00 y domingo 10:00). Va sobre el reloj de Costa Rica
reconstruido desde UTC, no sobre el del visitante: quien mire desde España o
Estados Unidos ve la hora de aquí, que es la que importa. Se refresca cada 30 s y
durante las dos horas siguientes al inicio cambia a «Transmitiendo ahora».

El último vídeo va en grande y el archivo completo en un panel lateral.

### Detalles que costaron más de lo que parecen

- **El botón de «Cómo llegar»** entrega la dirección al sistema en vez de
  imponer una app: en Android sale el selector, en iPhone abre Mapas de Apple, en
  computadora va a Google Maps. Con respaldo por si el esquema no responde.
- **Compatibilidad con Apple:** `color-mix()` pedía iOS 16.2 y se usaba en once
  sitios, varios estructurales. Reescritos a mano, el suelo bajó a iOS 15.
- **Las barras de scroll** salían con el aspecto nativo de Windows porque
  `scrollbar-width` y `::-webkit-scrollbar` no conviven y se pisaban. Ahora hay
  una sola regla para todo el sitio.

---

## Lo que falta

### Datos que hay que confirmar — **esto es lo que bloquea todo lo demás**

Hay contenido inventado para poder montar el diseño. **Está escrito como si
fuera cierto y no se distingue a simple vista.** Mientras no se confirme, el
sitio lleva `noindex` puesto a propósito para que no lo encuentre nadie.

1. **Los hitos de Historia de 2011, 2016 y 2021.** Inventados. Lo único
   confirmado es el arranque en 2005 y las más de veinte congregaciones.
2. **Las sedes del país** (`Iglesias bajo cobertura apostólica`): los cantones y
   horarios son inventados. Lo que vino confirmado fueron sólo las provincias.
3. **La dirección exacta de Tibás.** Ahora dice sólo «Tibás, San José, Costa
   Rica». Hace falta la dirección completa y, si se puede, el punto exacto en el
   mapa.

### Material

4. **Fotos del templo.** No hay ninguna del edificio.
5. **Fotos de En Vivo.** Sólo hay dos en la carpeta, y se nota en el collage.

### Técnico

6. **El «en vivo» real.** `tibas/worker/live.js` está escrito pero sin
   desplegar, y `CFG.liveEndpoint` sigue vacío. Hasta que se despliegue, el
   indicador rojo del encabezado es decorativo.
7. **Despliegue automático.** Hoy cada publicación se hace a mano con
   `wrangler`. Falta conectar el proyecto de Cloudflare Pages al repositorio de
   GitHub para que cada `push` publique solo. Las instrucciones están en
   `README.md`.
8. **Quitar el bloqueo de indexado** cuando los datos estén confirmados:
   `robots.txt` y la cabecera `X-Robots-Tag` en `_headers`.
9. **Borrar las previsualizaciones** `preview-intro.html` y `preview-pulso.html`
   de `public/` cuando ya no hagan falta: hoy se publican con el sitio.

---

## Cosas que conviene no olvidar

**El sitio se edita en `tibas/public/index.html` y en ningún otro sitio.** Hubo
una segunda copia en una carpeta `site/`; el 14/09 se copió la versión vieja
encima de la publicada y se perdieron ocho commits de trabajo, que hubo que
reconstruir mirando el historial. El 15/09 se eliminó esa copia. Una sola, y el
accidente no puede repetirse.

**Antes de desplegar, comparar con lo que hay publicado.** Cuesta diez segundos
y es exactamente lo que habría evitado lo anterior.

**Cloudflare cachea en el borde.** Tras publicar, verificar contra la URL
concreta del despliegue o añadiendo un parámetro cualquiera a la dirección. Si
no, se ve la versión vieja y parece que el despliegue falló.
