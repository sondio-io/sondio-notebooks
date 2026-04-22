# sondio-notebooks

Jupyter notebook gallery for the [Sondio](https://sondio.io) data platform.
Each notebook is a self-contained query-and-visualize example that uses the
[sondio](https://github.com/sondio-io/sondio-python) Python SDK end to end.

## Run in Colab

Every notebook runs unmodified in Google Colab:

1. Click the **Open in Colab** badge next to the notebook you want.
2. In Colab, open the 🔑 **Secrets** panel in the left sidebar.
3. Add a secret named `SONDIO_API_KEY` (toggle **Notebook access** on).
4. **Runtime → Run all**.

The setup cell installs `sondio` from PyPI and reads the key automatically.

> You'll need a free Sondio API key. Grab one at
> [sondio.io/developers](https://sondio.io/developers).

## Other platforms

The SDK's key resolution chain is: explicit `sondio.api_key = "..."` →
Colab Secrets → Kaggle Secrets → `SONDIO_API_KEY` environment variable →
`~/.sondio/config`. Pick whichever fits:

| Platform | How to provide the key |
|----------|------------------------|
| **Kaggle Kernels** | Add-ons → Secrets → `SONDIO_API_KEY` (toggle access) |
| **Deepnote**, **Hex**, **SageMaker Studio Lab**, **Paperspace**, **Noteable** | Use the platform's environment-variable / secret integration to set `SONDIO_API_KEY` |
| **Local Jupyter / VS Code** | Set `SONDIO_API_KEY` in your shell, or create `~/.sondio/config` with `[default]\napi_key = sk_sondio_...` |
| **Binder** | No built-in secrets — edit the first cell to inject the key manually (e.g. via `getpass`) |

In every case the notebook itself is unchanged; only where the key comes
from differs.

## Notebooks

### Energy

| Notebook | Open in Colab |
|----------|---------------|
| [Oil & gas production decline curve](energy/oilgas-production-trends.ipynb) — per-well monthly oil/gas/water over 15 years | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/energy/oilgas-production-trends.ipynb) |
| [US wind fleet density](energy/wind-turbine-density.ipynb) — USWTDB installed capacity by state + growth in turbine size | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/energy/wind-turbine-density.ipynb) |

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
| [SVI vs pipeline incidents](cross-vertical/svi-pipeline-incidents.ipynb) — state-level CDC SVI rollup compared to PHMSA incident rates | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sondio-io/sondio-notebooks/blob/main/cross-vertical/svi-pipeline-incidents.ipynb) |

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
