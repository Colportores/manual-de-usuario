# -*- coding: utf-8 -*-
"""Genera el sitio del manual de usuario de Colportaje a partir de su Markdown.

Uso (desde la raíz de este repo):

    pip install -r herramientas/requirements.txt
    python herramientas/generar.py [carpeta con el Markdown] [carpeta de salida]

Por defecto lee el Markdown de `fuente/` (README.md, colportor.md, coordinador.md, problemas-frecuentes.md y
glosario.md) y escribe el sitio en `_sitio/`, que no se guarda en git: lo arma el workflow de GitHub Actions y lo
publica en GitHub Pages. Con otra carpeta de origen se usa su `imagenes/` si la tiene y, si no, la de la raíz.

Entradas del sitio: `estilo.css`, `fuentes/` e `imagenes/` (en la raíz del repo). Al terminar, el script revisa
que no haya enlaces, anclas ni imágenes rotas y, si las hay, falla con código 1.

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
    # en el Markdown las imágenes se enlazan como ../imagenes/ (para que se vean en GitHub); en el sitio, ./imagenes/
    texto = texto.replace('src="../imagenes/', 'src="./imagenes/')
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


def verificar(salida):
    """Falla si alguna página enlaza un archivo, una ancla o una imagen que no existe."""
    paginas = {}
    for _, nombre, _ in DOCS:
        paginas[nombre] = io.open(os.path.join(salida, nombre), encoding="utf-8").read()
    anclas = {n: set(re.findall(r'\bid="([^"]+)"', h)) for n, h in paginas.items()}
    errores, imagenes = [], 0
    for nombre, html in paginas.items():
        for atributo, valor in re.findall(r'\b(href|src)="([^"]*)"', html):
            if valor.startswith(("http://", "https://", "data:", "mailto:")):
                continue
            ruta, _, ancla_ = valor.partition("#")
            ruta = ruta[2:] if ruta.startswith("./") else ruta
            destino = ruta or nombre
            if ruta and not os.path.exists(os.path.join(salida, ruta)):
                errores.append('%s: %s="%s" no existe' % (nombre, atributo, valor))
            elif ancla_ and destino in anclas and ancla_ not in anclas[destino]:
                errores.append("%s: el ancla #%s no existe en %s" % (nombre, ancla_, destino))
            if atributo == "src" and ruta.startswith("imagenes/"):
                imagenes += 1
    existentes = sum(len(archivos) for _, _, archivos in os.walk(os.path.join(salida, "imagenes")))
    print("Imágenes referenciadas: %d; en el sitio: %d; enlaces rotos: %d" % (imagenes, existentes, len(errores)))
    if errores:
        sys.exit("Hay enlaces o imágenes rotas:\n  " + "\n  ".join(errores))
    if imagenes != existentes:
        sys.exit("Las imágenes referenciadas (%d) no son las que hay en el sitio (%d)." % (imagenes, existentes))


def main():
    origen = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RAIZ, "fuente")
    salida = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(RAIZ, "_sitio")
    if not os.path.isdir(origen):
        sys.exit("No existe la carpeta con el Markdown: %s" % origen)
    if os.path.isdir(salida):
        shutil.rmtree(salida)
    os.makedirs(salida)
    for md_nombre, html_nombre, _ in DOCS:
        texto = io.open(os.path.join(origen, md_nombre), encoding="utf-8").read()
        app = "coordinador" if "coordinador" in md_nombre else "colportor"
        io.open(os.path.join(salida, html_nombre), "w", encoding="utf-8", newline="\n").write(
            convertir(texto, html_nombre, app))
    shutil.copy(os.path.join(RAIZ, "estilo.css"), os.path.join(salida, "estilo.css"))
    shutil.copytree(os.path.join(RAIZ, "fuentes"), os.path.join(salida, "fuentes"))
    imagenes = os.path.join(origen, "imagenes")
    if not os.path.isdir(imagenes):
        imagenes = os.path.join(RAIZ, "imagenes")
    shutil.copytree(imagenes, os.path.join(salida, "imagenes"))
    io.open(os.path.join(salida, ".nojekyll"), "w").close()  # Pages no debe pasar el sitio por Jekyll
    verificar(salida)
    print("Sitio generado en", salida)


if __name__ == "__main__":
    main()
