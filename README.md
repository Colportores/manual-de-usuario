# Manual de usuario de Colportaje

Sitio del manual de usuario: la app del teléfono para el colportor y el panel web para el coordinador, paso a paso y con capturas.

**Para leerlo:** https://colportores.github.io/manual-de-usuario/

| Página | Para quién |
|---|---|
| [Manual del colportor](https://colportores.github.io/manual-de-usuario/colportor.html) | Colportores |
| [Manual del coordinador](https://colportores.github.io/manual-de-usuario/coordinador.html) | Coordinadores |
| [Problemas frecuentes](https://colportores.github.io/manual-de-usuario/problemas-frecuentes.html) | Todos |
| [Glosario](https://colportores.github.io/manual-de-usuario/glosario.html) | Todos |

Todas las personas, direcciones, correos y montos que se ven en las capturas son de ejemplo.

## Cómo está armado

Este repo tiene el texto del manual (Markdown) y el generador del sitio. El texto se edita acá, en `fuente/`; el repo de documentación de la organización solo lo referencia. El HTML no se guarda en git: lo arma y lo publica un workflow de GitHub Actions.

- `fuente/`: el texto del manual en Markdown (`README.md` es la portada, más `colportor.md`, `coordinador.md`, `problemas-frecuentes.md` y `glosario.md`). Las capturas se enlazan como `../imagenes/...`, así también se ven al leer el Markdown en GitHub.
- `imagenes/`: las capturas.
- `estilo.css`: el estilo, con los colores y las tipografías de la app.
- `fuentes/`: Inter, Source Serif 4 y JetBrains Mono, con su licencia (SIL Open Font License).
- `herramientas/generar.py`: arma el sitio completo en `_sitio/` (una página `.html` por documento, más el estilo, las tipografías y las capturas) y falla si queda algún enlace, ancla o imagen rota.
- `.github/workflows/publicar.yml`: valida el manual en cada pull request y, al llegar a `main`, genera el sitio y lo publica en GitHub Pages.

## Cómo actualizarlo

1. Editá el Markdown de `fuente/` (y agregá las capturas nuevas en `imagenes/`).
2. Abrí un pull request a `main`. El workflow arma el sitio y falla si hay enlaces o imágenes rotas.
3. Al mergear a `main`, el workflow lo publica solo en https://colportores.github.io/manual-de-usuario/ (tarda uno o dos minutos). No hace falta generar ni subir ningún `.html`.

Para ver el resultado en tu máquina antes del pull request:

```bash
pip install -r herramientas/requirements.txt
python herramientas/generar.py                 # lee fuente/ y escribe _sitio/
python herramientas/generar.py <otra carpeta>  # opcional: otra carpeta con el Markdown
```

Abrí `_sitio/index.html` en el navegador. La carpeta `_sitio/` no se sube a git.
