# Ministerios Ebenezer Costa Rica — sitios web

Monorepo con los sitios de las congregaciones de Ministerios Ebenezer en Costa Rica.
Cada iglesia vive en su propia carpeta y se despliega como un proyecto independiente
de Cloudflare Pages, así una puede actualizarse sin tocar a las demás.

```
tibas/          Iglesia madre — San José, Tibás        [en línea]
```

Congregaciones previstas para más adelante: Alajuela, Cartago, Limón, Heredia,
Puntarenas y Guanacaste.

## Cómo se añade una iglesia nueva

1. Copiar `tibas/` con el nombre del cantón o la provincia.
2. Ajustar contenido, dirección y horarios dentro de `<carpeta>/public/index.html`
   (los datos están en constantes al principio del `<script>`: `SERVICIOS`, `HISTORIA`,
   `DEPTOS`, `DIRECCION`, `SEDES` y `CFG` con los enlaces de YouTube y Facebook).
3. Crear un proyecto nuevo de Cloudflare Pages apuntando a este mismo repositorio,
   con **Root directory** = la carpeta de esa iglesia.

## Despliegue en Cloudflare Pages

**Workers & Pages → Create → Pages → Connect to Git**, elegir este repositorio:

| Campo | Valor |
|---|---|
| Project name | `iebenezer-tibas` |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | *(vacío)* |
| Build output directory | `public` |
| Root directory | `tibas` |

No hay build ni dependencias: los sitios son HTML estático autocontenido. Cada `git push`
a `main` publica automáticamente.

## Estado

Despliegue de prueba. Cada sitio lleva `robots.txt` y la cabecera `X-Robots-Tag: noindex`
para que los buscadores no lo recojan mientras haya contenido sin confirmar. Los pendientes
de cada iglesia están en su propio README.
