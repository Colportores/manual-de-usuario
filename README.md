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

Este repo tiene solo el sitio ya generado. El texto del manual se escribe en Markdown en el repo de documentación de la organización (`docs/manual-usuario/`); acá no se edita a mano ningún `.html`.

- `index.html`, `colportor.html`, `coordinador.html`, `problemas-frecuentes.html`, `glosario.html`: las páginas.
- `estilo.css`: el estilo, con los colores y las tipografías de la app.
- `imagenes/`: las capturas.
- `fuentes/`: Inter, Source Serif 4 y JetBrains Mono, con su licencia (SIL Open Font License).
- `herramientas/generar.py`: el script que arma todo lo anterior a partir del Markdown.

## Cómo actualizarlo

Cuando cambia el Markdown del manual:

```bash
pip install -r herramientas/requirements.txt
python herramientas/generar.py <ruta a docs/manual-usuario del repo de documentación>
git add -A
git commit -m "docs: actualizar el manual"
git push
```

GitHub Pages publica solo lo que está en la rama `main`; el cambio se ve en uno o dos minutos.
