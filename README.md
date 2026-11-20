# diegoamaya-web

Sitio personal de Diego Germán Amaya — https://www.diegoamaya.com.ar (español) y /en/ (inglés).

Sitio estático. Vercel publica los archivos tal cual, sin compilar.

## Estructura
- `src/index.html` — plantilla de origen. Todo el contenido está en el objeto `SITE_ES` (español) y `SITE_EN_OVERLAY` (inglés), al comienzo del `<script>`.
- `build.py` — genera `index.html` y `en/index.html` con el contenido ya escrito en el HTML (para buscadores).
- `images/`, íconos, `robots.txt`, `sitemap.xml`.

## Editar contenido
1. Editar `src/index.html` (si se agrega un ítem en español, agregar su traducción en la misma posición de `SITE_EN_OVERLAY`).
2. Ejecutar `python3 build.py` (requiere Playwright: `pip install playwright && playwright install chromium`).
3. Subir los cambios. Vercel publica solo.

No editar `index.html` ni `en/index.html` a mano: se regeneran con `build.py`.
