# sondio-notebooks

Jupyter notebook gallery for the [Sondio](https://sondio.io) data platform.
Each notebook is a self-contained query-and-visualize example that uses the
[sondio](https://github.com/sondio-io/sondio-python) Python SDK end to end.

## Run in Colab

Every notebook runs unmodified in Google Colab — click the badge next to the
one you want, set `SONDIO_API_KEY` in the Colab secrets panel (🔑 sidebar),
and **Runtime → Run all**.

> You'll need a free Sondio API key. Grab one at
> [sondio.io/developers](https://sondio.io/developers).

## Notebooks

### Environmental

| Notebook | Open in Colab |
|----------|---------------|
| [UIC aquifer exemptions near population](env/aquifer-exemptions-near-population.ipynb) — EPA UIC exemption locations + depths in Texas | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/env/aquifer-exemptions-near-population.ipynb) |
| [GHG facility emissions choropleth](env/ghg-facility-heatmap.ipynb) — EPA GHGRP CO₂e aggregated to the state level | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/env/ghg-facility-heatmap.ipynb) |

### Cross-vertical

| Notebook | Open in Colab |
|----------|---------------|
| [Earthquake + well proximity](cross-vertical/earthquake-well-proximity.ipynb) — TX wells within 20 miles of the strongest recent M3+ quake | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/cross-vertical/earthquake-well-proximity.ipynb) |
| [Pipeline safety explorer](cross-vertical/pipeline-safety-explorer.ipynb) — PHMSA incidents by state, drill into Texas | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/cross-vertical/pipeline-safety-explorer.ipynb) |

## Authoring

Notebooks here are built deterministically from Python source in
`tools/build_notebooks.py` so the repo stays free of committed output cells.
Regenerate with:

```bash
python tools/build_notebooks.py
```

To add a new notebook, write a builder function next to the existing ones
and register it in `main()`.

## License

MIT — see [LICENSE](LICENSE).
