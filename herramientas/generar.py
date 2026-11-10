# -*- coding: utf-8 -*-
"""Genera el sitio del manual de usuario de Colportaje a partir de su Markdown.

Uso (desde la raíz de este repo):

    pip install -r herramientas/requirements.txt
    python herramientas/generar.py <carpeta con el Markdown del manual>

La carpeta de origen es `docs/manual-usuario/` del repo de documentación: tiene README.md, colportor.md,
coordinador.md, problemas-frecuentes.md, glosario.md y la carpeta imagenes/. El script escribe en la raíz de este
repo un .html por documento, estilo.css y la copia de imagenes/. Las fuentes ya están en fuentes/.

El estilo sigue el tema de la app: navy #002856 sobre crema #FAFAF7, títulos en Source Serif 4, texto en Inter y
rótulos en JetBrains Mono.
"""
import io
import os
import re
import shutil
import sys

import markdown

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS = [
    ("README.md", "index.html", "Inicio"),
    ("colportor.md", "colportor.html", "Colportor"),
    ("coordinador.md", "coordinador.html", "Coordinador"),
    ("problemas-frecuentes.md", "problemas-frecuentes.html", "Problemas frecuentes"),
    ("glosario.md", "glosario.html", "Glosario"),
]


def ancla(valor, separador="-"):
    """El mismo criterio de GitHub para las anclas de los títulos."""
    t = valor.strip().lower()
    t = re.sub(r"[^\w\s-]", "", t, flags=re.U)
    return re.sub(r"\s", separador, t)


CSS = r"""
@font-face { font-family: "Inter"; src: url("fuentes/Inter.ttf") format("truetype"); font-weight: 100 900; }
@font-face { font-family: "Source Serif 4"; src: url("fuentes/SourceSerif4.ttf") format("truetype"); font-weight: 200 900; }
@font-face { font-family: "JetBrains Mono"; src: url("fuentes/JetBrainsMono.ttf") format("truetype"); font-weight: 100 800; }

:root {
  --navy: #002856; --navy-hover: #13407A; --tinta: #0E1A2B; --texto-2: #2A3A52; --gris: #5B6B82;
  --placeholder: #90A0B7; --borde: #E3E7EE; --borde-input: #CFD6E1; --crema: #FAFAF7; --superficie: #FFFFFF;
  --relleno: #F3F1EA; --rojo: #B00020; --verde: #2F6B3A; --verde-fondo: #DDE9D8; --ambar: #7A5A12;
  --ambar-fondo: #FCEFD9; --azul-fondo: #E4ECF7;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 84px; }
body { margin: 0; background: var(--crema); color: var(--tinta); font: 16px/1.62 "Inter", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased; }
a { color: var(--navy-hover); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { color: var(--navy); }

.barra { position: sticky; top: 0; z-index: 10; background: rgba(250, 250, 247, .94); backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--borde); }
.barra-int { max-width: 1280px; margin: 0 auto; padding: 14px 28px; display: flex; align-items: center; gap: 18px;
  flex-wrap: wrap; }
.marca { display: flex; align-items: center; gap: 12px; text-decoration: none; color: var(--tinta); }
.marca i { width: 26px; height: 26px; border-radius: 7px; background: var(--navy); display: block; }
.marca b { font: 600 10.5px/1 "JetBrains Mono", monospace; letter-spacing: 2px; color: var(--texto-2); }
.marca span { font: 600 17px/1 "Source Serif 4", serif; }
.nav { margin-left: auto; display: flex; gap: 6px; flex-wrap: wrap; }
.nav a { padding: 8px 14px; border-radius: 999px; font-weight: 600; font-size: 13.5px; color: var(--texto-2);
  text-decoration: none; border: 1px solid transparent; }
.nav a:hover { border-color: var(--borde-input); }
.nav a.actual { background: var(--navy); color: #fff; }

.pagina { max-width: 1280px; margin: 0 auto; padding: 0 28px 96px; display: grid;
  grid-template-columns: 270px minmax(0, 1fr); gap: 56px; }
.indice { position: sticky; top: 74px; align-self: start; max-height: calc(100vh - 90px); overflow: auto;
  padding: 28px 6px 28px 0; font-size: 13.5px; }
.indice .rotulo, .rotulo { font: 600 10.5px/1.3 "JetBrains Mono", monospace; letter-spacing: 1.6px;
  text-transform: uppercase; color: var(--gris); }
.indice ul { list-style: none; margin: 12px 0 0; padding: 0; }
.indice li { margin: 0; }
.indice a { display: block; padding: 6px 10px; border-radius: 9px; color: var(--texto-2); text-decoration: none;
  line-height: 1.35; }
.indice a:hover { background: var(--relleno); color: var(--navy); }
.indice .n2 > a { font-weight: 700; color: var(--tinta); margin-top: 10px; }
.indice .n3 > a { padding-left: 20px; color: var(--gris); }

main { padding-top: 44px; min-width: 0; max-width: 860px; }
h1 { font: 600 44px/1.12 "Source Serif 4", serif; letter-spacing: -.4px; margin: 6px 0 18px; }
h2 { font: 600 32px/1.18 "Source Serif 4", serif; letter-spacing: -.2px; margin: 76px 0 14px; padding-top: 30px;
  border-top: 1px solid var(--borde); }
h3 { font: 600 23px/1.25 "Source Serif 4", serif; margin: 56px 0 10px; }
h4 { font: 700 16.5px/1.3 "Inter", sans-serif; margin: 36px 0 8px; }
h2 .num, h3 .num { display: block; font: 600 10.5px/1 "JetBrains Mono", monospace; letter-spacing: 2px;
  text-transform: uppercase; color: var(--gris); margin-bottom: 10px; }
p { margin: 0 0 14px; color: var(--texto-2); }
main > p:first-of-type { font-size: 17.5px; }
strong { color: var(--tinta); }
p.rotulo { margin: 28px 0 10px; }
code { font: 500 .88em "JetBrains Mono", monospace; background: var(--relleno); border: 1px solid var(--borde);
  border-radius: 6px; padding: 1px 6px; color: var(--tinta); }

ul, ol { margin: 0 0 16px; padding-left: 22px; color: var(--texto-2); }
li { margin: 6px 0; }
main ol { list-style: none; counter-reset: paso; padding-left: 0; }
main ol > li { counter-increment: paso; position: relative; padding: 2px 0 2px 44px; margin: 10px 0; }
main ol > li::before { content: counter(paso); position: absolute; left: 0; top: 1px; width: 28px; height: 28px;
  border-radius: 50%; background: var(--navy); color: #fff; font: 700 12.5px/28px "Inter", sans-serif;
  text-align: center; }
main ol ul { margin: 6px 0 2px; }

blockquote { margin: 20px 0; padding: 14px 18px; border-radius: 14px; background: var(--superficie);
  border: 1.5px solid var(--navy); }
blockquote p { margin: 0; color: var(--tinta); font-size: 15px; }
blockquote.proximamente { background: var(--ambar-fondo); border-color: var(--ambar); }
blockquote.proximamente p, blockquote.proximamente strong { color: #5C430B; }
blockquote.importante { background: var(--superficie); border-color: var(--navy); }
blockquote.consejo { background: var(--verde-fondo); border-color: var(--verde); }
blockquote.consejo p, blockquote.consejo strong { color: #1F4D29; }

.tabla { margin: 14px 0 24px; background: var(--superficie); border: 1px solid var(--borde); border-radius: 16px;
  overflow: hidden; overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
th { text-align: left; font: 600 10.5px/1.3 "JetBrains Mono", monospace; letter-spacing: 1.4px;
  text-transform: uppercase; color: var(--gris); padding: 14px 18px 10px; background: var(--crema);
  border-bottom: 1px solid var(--borde); }
td { padding: 13px 18px; vertical-align: top; border-top: 1px solid var(--borde); color: var(--texto-2); }
tr:first-child td { border-top: 0; }
td:first-child { color: var(--tinta); font-weight: 500; }

.galeria { display: flex; flex-wrap: wrap; gap: 26px 22px; margin: 22px 0 30px; padding: 26px 24px;
  background: var(--relleno); border-radius: 22px; justify-content: center; }
figure { margin: 0; }
figure.telefono { width: 244px; }
figure.telefono img { display: block; width: 100%; height: auto; border-radius: 24px; background: #fff;
  border: 1px solid var(--borde-input); box-shadow: 0 1px 2px rgba(14, 26, 43, .06), 0 14px 30px -14px rgba(0, 40, 86, .28); }
figure.telefono.recorte img { border-radius: 14px; }
figure.pantalla { width: 100%; }
figure.pantalla .marco { border-radius: 14px; overflow: hidden; border: 1px solid var(--borde-input);
  background: #fff; box-shadow: 0 1px 2px rgba(14, 26, 43, .06), 0 18px 36px -18px rgba(0, 40, 86, .3); }
figure.pantalla .marco::before { content: "• • •"; display: block; padding: 5px 14px 6px; color: var(--placeholder);
  font-size: 15px; letter-spacing: 1px; background: var(--crema); border-bottom: 1px solid var(--borde); }
figure.pantalla img { display: block; width: 100%; height: auto; }
figcaption { margin-top: 10px; font-size: 12px; line-height: 1.4; color: var(--gris); text-align: center; }

.portada { margin: 8px 0 34px; padding: 40px 40px 36px; border-radius: 26px; background: var(--navy); color: #fff; }
.portada .rotulo { color: #B9C7DC; }
.portada h1 { color: #fff; margin: 14px 0 12px; }
.portada p { color: #DCE4F0; font-size: 17px; margin: 0; max-width: 620px; }
.pie { margin-top: 80px; padding-top: 22px; border-top: 1px solid var(--borde); font-size: 12.5px; color: var(--gris); }

.indice-movil { display: none; margin: 18px 0 26px; background: var(--superficie); border: 1px solid var(--borde);
  border-radius: 16px; padding: 4px 16px; font-size: 14.5px; }
.indice-movil summary { cursor: pointer; padding: 12px 0; font-weight: 700; color: var(--navy); }
.indice-movil ul { list-style: none; margin: 0 0 12px; padding: 0; }
.indice-movil li { margin: 0; }
.indice-movil a { display: block; padding: 9px 0; text-decoration: none; color: var(--texto-2);
  border-top: 1px solid var(--borde); }
.indice-movil .n2 > a { font-weight: 700; color: var(--tinta); }
.indice-movil .n3 > a { padding-left: 16px; }

@media (max-width: 980px) {
  html { scroll-padding-top: 112px; }
  .pagina { grid-template-columns: 1fr; gap: 0; padding: 0 16px 72px; }
  .indice { display: none; }
  .indice-movil { display: block; }
  .barra-int { padding: 10px 16px 8px; gap: 8px; }
  .nav { margin-left: 0; width: 100%; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; gap: 2px; }
  .nav::-webkit-scrollbar { display: none; }
  .nav a { white-space: nowrap; padding: 7px 12px; font-size: 13px; }
  main { padding-top: 26px; }
  h1 { font-size: 34px; } h2 { font-size: 26px; margin-top: 56px; } h3 { font-size: 20px; margin-top: 44px; }
  .galeria { padding: 18px 12px; gap: 20px 12px; }
  figure.telefono { width: 46%; min-width: 150px; }
  .portada { padding: 28px 22px; }
}
@media (max-width: 640px) {
  .tabla { border-radius: 14px; }
  table, tbody, tr, td { display: block; width: 100%; }
  thead { display: none; }
  tr { padding: 12px 16px; border-top: 1px solid var(--borde); }
  tbody tr:first-child { border-top: 0; }
  td, tr:first-child td { border: 0; padding: 4px 0; }
  td::before { content: attr(data-th); display: block; font: 600 10px/1.4 "JetBrains Mono", monospace;
    letter-spacing: 1.3px; text-transform: uppercase; color: var(--gris); margin-top: 4px; }
  td[data-th=""]::before { display: none; }
}
"""

PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · Manual de usuario de Colportaje</title>
<meta name="description" content="Manual de usuario de Colportaje: la app del colportor y el panel del coordinador, paso a paso y con capturas.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23002856'/%3E%3C/svg%3E">
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<header class="barra"><div class="barra-int">
  <a class="marca" href="index.html"><i></i><b>COLPORTAJE</b><span>Manual de usuario</span></a>
  <nav class="nav">{nav}</nav>
</div></header>
<div class="pagina">
  <aside class="indice"><div class="rotulo">En esta página</div><ul>{indice}</ul></aside>
  <main>
{cuerpo}
  <div class="pie">Manual de usuario de Colportaje · versión de la app de noviembre de 2026 · todas las personas, direcciones y montos de las capturas son de ejemplo.</div>
  </main>
</div>
</body>
</html>
"""

ROTULOS = ("Pasos", "Antes de empezar", "Qué puede pasar", "Qué vas a ver", "Para qué sirve", "Cómo se llega")


def convertir(texto, salida_html, app):
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": ancla, "toc_depth": "2-3"}})
    # dos avisos seguidos son dos recuadros (python-markdown los une si solo los separa una línea en blanco)
    texto = re.sub(r"(^>[^\n]*\n)\n(?=>)", "\\1\n<!-- -->\n\n", texto, flags=re.M)
    html = md.convert(texto)

    # enlaces entre documentos
    for origen, destino, _ in DOCS:
        html = html.replace('href="./%s' % origen, 'href="%s' % destino).replace('href="%s' % origen, 'href="%s' % destino)

    # el índice plano del Markdown sobra: lo reemplaza el índice lateral
    html = re.sub(r'<h2 id="contenido">.*?</h2>\s*<ul>.*?</ul>', "", html, count=1, flags=re.S)

    # galerías de capturas
    def galeria(m):
        figs = []
        for im in re.finditer(r'<img\s+src="([^"]+)"\s+alt="([^"]*)"(?:\s+width="(\d+)")?\s*/?>', m.group(1)):
            src, alt, ancho = im.group(1), im.group(2), int(im.group(3) or 0)
            if "/coordinador/" in src:
                figs.append('<figure class="pantalla"><div class="marco"><img loading="lazy" src="%s" alt="%s"></div>'
                            '<figcaption>%s</figcaption></figure>' % (src, alt, alt))
            else:
                figs.append('<figure class="telefono"><img loading="lazy" src="%s" alt="%s">'
                            '<figcaption>%s</figcaption></figure>' % (src, alt, alt))
        return '<div class="galeria">%s</div>' % "".join(figs)

    html = re.sub(r'<p align="center">(.*?)</p>', galeria, html, flags=re.S)

    # avisos
    def aviso(m):
        cuerpo = m.group(1)
        clase = "importante"
        if re.search(r"<strong>Próximamente", cuerpo):
            clase = "proximamente"
        elif re.search(r"<strong>(Consejo|Tip|Dato)", cuerpo):
            clase = "consejo"
        return '<blockquote class="%s">%s</blockquote>' % (clase, cuerpo)

    html = re.sub(r"<blockquote>(.*?)</blockquote>", aviso, html, flags=re.S)

    # rótulos «Pasos», «Qué puede pasar»…
    for r in ROTULOS:
        html = html.replace("<p><strong>%s</strong></p>" % r, '<p class="rotulo">%s</p>' % r)
        html = html.replace("<p><strong>%s:</strong></p>" % r, '<p class="rotulo">%s</p>' % r)

    # los pasos que siguen después de una imagen conservan su número
    html = re.sub(r'<ol start="(\d+)">',
                  lambda m: '<ol start="%s" style="counter-reset: paso %d">' % (m.group(1), int(m.group(1)) - 1), html)

    # tablas en tarjeta; cada celda lleva el título de su columna para apilarlas en el teléfono
    def tabla(m):
        cuerpo = m.group(1)
        titulos = [re.sub(r"<[^>]+>", "", t).strip() for t in re.findall(r"<th[^>]*>(.*?)</th>", cuerpo, re.S)]

        def fila(f):
            n = [0]

            def celda(c):
                rotulo = titulos[n[0]] if n[0] < len(titulos) else ""
                n[0] += 1
                return '<td data-th="%s"%s>' % (rotulo.replace('"', "&quot;"), c.group(1))

            return re.sub(r"<td([^>]*)>", celda, f.group(0))

        cuerpo = re.sub(r"<tr>.*?</tr>", fila, cuerpo, flags=re.S)
        return '<div class="tabla"><table>%s</table></div>' % cuerpo

    html = re.sub(r"<table>(.*?)</table>", tabla, html, flags=re.S)

    # número de capítulo y de sección como rótulo
    html = re.sub(r'(<h2 id="[^"]*">)(\d+)\. ', r'\1<span class="num">Capítulo \2</span>', html)
    html = re.sub(r'(<h3 id="[^"]*">)(\d+\.\d+) ', r'\1<span class="num">\2</span>', html)

    # portada en el índice
    titulo = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    titulo_txt = re.sub(r"<[^>]+>", "", titulo.group(1)) if titulo else "Manual de usuario"
    if salida_html == "index.html" and titulo:
        intro = re.search(r"</h1>\s*<p>(.*?)</p>", html, re.S)
        portada = ('<div class="portada"><div class="rotulo">Colportaje · noviembre de 2026</div>'
                   "<h1>Manual de usuario</h1><p>Paso a paso y con capturas: la app del teléfono para el colportor "
                   "y el panel web para el coordinador.</p></div>")
        html = html.replace(titulo.group(0), portada, 1)

    # índice lateral
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]*)">(.*?)</h\1>', html, re.S):
        txt = re.sub(r'<span class="num">.*?</span>', "", m.group(3))
        txt = re.sub(r"<[^>]+>", "", txt)
        items.append('<li class="n%s"><a href="#%s">%s</a></li>' % (m.group(1), m.group(2), txt))

    nav = "".join('<a href="%s"%s>%s</a>' % (d, ' class="actual"' if d == salida_html else "", n)
                  for _, d, n in DOCS if d != "index.html")
    # en pantallas angostas el índice lateral no entra: va plegado arriba del texto
    if len(items) > 3:
        plegado = ('<details class="indice-movil"><summary>Índice de esta página</summary><ul>%s</ul></details>'
                   % "".join(items))
        if "</h1>" in html:
            html = html.replace("</h1>", "</h1>" + plegado, 1)
        else:
            html = html.replace("</div>", "</div>" + plegado, 1)
    return PLANTILLA.format(titulo=titulo_txt, nav=nav, indice="".join(items), cuerpo=html)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origen, salida = sys.argv[1], RAIZ
    for md_nombre, html_nombre, _ in DOCS:
        texto = io.open(os.path.join(origen, md_nombre), encoding="utf-8").read()
        app = "coordinador" if "coordinador" in md_nombre else "colportor"
        io.open(os.path.join(salida, html_nombre), "w", encoding="utf-8", newline="\n").write(
            convertir(texto, html_nombre, app))
    io.open(os.path.join(salida, "estilo.css"), "w", encoding="utf-8", newline="\n").write(CSS.lstrip())
    destino = os.path.join(salida, "imagenes")
    if os.path.isdir(destino):
        shutil.rmtree(destino)
    shutil.copytree(os.path.join(origen, "imagenes"), destino)
    print("Sitio generado en", salida)


if __name__ == "__main__":
    main()
