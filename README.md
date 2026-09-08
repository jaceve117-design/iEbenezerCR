# Ministerios Ebenezer Costa Rica — sitio web

Sitio de una sola página. Sin build, sin dependencias que instalar: `public/index.html`
es autocontenido (el logo va incrustado como data URI; tipografía y GSAP se cargan por CDN).

```
public/          ← lo que publica Cloudflare Pages
  index.html     el sitio completo
  _headers       cabeceras de seguridad + noindex mientras es prueba
  robots.txt     bloqueo de indexado mientras es prueba
worker/
  live.js        Cloudflare Worker para el estado real de la transmisión
```

## Desplegar en Cloudflare Pages

En el panel de Cloudflare → **Workers & Pages → Create → Pages → Connect to Git**,
elegí este repositorio y configurá:

| Campo | Valor |
|---|---|
| Framework preset | **None** |
| Build command | *(vacío)* |
| Build output directory | `public` |
| Root directory | *(vacío)* |

Cada `git push` a `main` publica automáticamente.

### Alternativa sin GitHub

```bash
npx wrangler pages deploy public --project-name ebenezer-cr
```

## Antes del lanzamiento real

- [ ] Quitar `public/robots.txt` y la línea `X-Robots-Tag` de `public/_headers`
- [ ] Fotografía propia del templo y la congregación (hoy son miniaturas de YouTube)
- [ ] Dirección exacta y enlace fijado de Google Maps
- [ ] Confirmar los hitos de historia de 2011, 2016 y 2021
- [ ] Confirmar cantones y horarios de las sedes de provincia
- [ ] Enlaces reales de descarga de Rhema y de las aplicaciones
- [ ] Desplegar `worker/live.js` y pegar su URL en `CFG.liveEndpoint` dentro de `index.html`

## El Worker de transmisión

Da el estado real de En Vivo (badge EN VIVO/OFFLINE, título de la transmisión, último
video). Sin él, el sitio funciona igual en modo de reserva: intenta el embed
`live_stream` y a los 4 s cae a la lista de subidas del canal.

Las instrucciones de despliegue están en la cabecera de `worker/live.js`. La API key
vive como secreto del Worker y nunca llega al navegador.
