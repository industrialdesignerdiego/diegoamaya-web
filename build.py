"""
Compila el sitio: toma src/index.html (plantilla con el contenido en el objeto SITE)
y genera páginas con todo el contenido ya escrito en el HTML, para buscadores:

  index.html     → español (www.diegoamaya.com.ar/)
  en/index.html  → inglés  (www.diegoamaya.com.ar/en/)

Uso:  python3 build.py   (requiere Playwright y Chromium)
Después de editar src/index.html, volver a correr este script antes de subir los cambios.
"""
import json
import pathlib
import re

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
SRC = (ROOT / "src" / "index.html").as_uri()
SITE_URL = "https://www.diegoamaya.com.ar/"

EN_HEAD = {
    '<link rel="canonical" href="https://www.diegoamaya.com.ar/">': '<link rel="canonical" href="https://www.diegoamaya.com.ar/en/">',
    '<meta property="og:url" content="https://www.diegoamaya.com.ar/">': '<meta property="og:url" content="https://www.diegoamaya.com.ar/en/">',
    '<meta property="og:locale" content="es_AR">': '<meta property="og:locale" content="en_US">',
    '<meta property="og:title" content="Diego Amaya | Diseño Industrial, Docencia e Investigación">': '<meta property="og:title" content="Diego Amaya | Industrial Design, Teaching and Research">',
    '<meta property="og:description" content="Diseñador industrial, MBA y doctorando en Diseño. Investigación, docencia, fabricación digital e Industria 4.0.">': '<meta property="og:description" content="Industrial designer, MBA, Master\'s in AI and PhD candidate in Design. Research, teaching, digital fabrication and Industry 4.0.">',
    '<meta property="og:description" content="Diseñador industrial, MBA, máster en IA y doctorando en Diseño. Investigación, docencia, fabricación digital e Industria 4.0.">': '<meta property="og:description" content="Industrial designer, MBA, Master\'s in AI and PhD candidate in Design. Research, teaching, digital fabrication and Industry 4.0.">',
}


def clean_state(page):
    """Quita estados que dependen del scroll o de la interacción."""
    page.evaluate("""() => {
      document.querySelector('.site-header')?.classList.remove('scrolled');
      document.querySelector('#toTop')?.classList.remove('show');
      document.querySelectorAll('.tl-item.reached').forEach(n => n.classList.remove('reached'));
      const pr = document.querySelector('#timeline .progress'); if (pr) pr.removeAttribute('style');
      document.querySelectorAll('#nav a[aria-current]').forEach(a => a.removeAttribute('aria-current'));
    }""")


def build():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome") if pathlib.Path("/usr/bin/google-chrome").exists() else p.chromium.launch()

        # Textos fijos en español, tomados de la plantilla
        page = browser.new_page()
        page.goto(SRC)
        page.wait_for_timeout(300)
        static_es, static_attr_es = page.evaluate("() => [STATIC_ES, STATIC_ATTR_ES]")
        page.close()

        for lang, root, out in [("es", "", ROOT / "index.html"), ("en", "../", ROOT / "en" / "index.html")]:
            page = browser.new_page(viewport={"width": 1366, "height": 900})
            page.add_init_script(f"window.__LANG={json.dumps(lang)};window.__ROOT={json.dumps(root)};")
            page.goto(SRC)
            page.wait_for_timeout(500)
            clean_state(page)
            html = "<!DOCTYPE html>\n" + page.evaluate("() => document.documentElement.outerHTML")
            page.close()

            boot = (f"<script>window.__LANG={json.dumps(lang)};window.__ROOT={json.dumps(root)};"
                    f"window.__STATIC_ES={json.dumps(static_es, ensure_ascii=False)};"
                    f"window.__STATIC_ATTR_ES={json.dumps(static_attr_es, ensure_ascii=False)};</script>")
            html = html.replace("<head>", "<head>\n" + boot, 1)

            if lang == "es":
                html = html.replace('href="./" data-lang="es"', 'href="./" data-lang="es"').replace('href="en/" data-lang="en"', 'href="en/" data-lang="en"')
            else:
                for a, b in EN_HEAD.items():
                    html = html.replace(a, b)
                html = html.replace('href="./" data-lang="es"', 'href="../" data-lang="es"').replace('href="en/" data-lang="en"', 'href="./" data-lang="en"')
                # Rutas relativas de archivos propios desde /en/
                html = re.sub(r'(src|srcset|href)="(images/|favicon|apple-touch-icon)', r'\1="../\2', html)
                html = re.sub(r'(srcset="[^"]*?), images/', r'\1, ../images/', html)

            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print(f"{lang}: {out.relative_to(ROOT)} ({len(html)//1024} KB)")
        browser.close()


if __name__ == "__main__":
    build()
