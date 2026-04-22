"""Build the starter notebooks.

Notebooks are authored here as code (via nbformat) so the repo never stores
executed outputs. Run `python tools/build_notebooks.py` to regenerate the
.ipynb files under energy/, env/, and cross-vertical/.
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

REPO_ROOT = Path(__file__).resolve().parent.parent


def _nb(cells: list) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    return nb


def _md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def _code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source)


SETUP_CELL = (
    "# First run only: install the SDK.\n"
    "# %pip install 'sondio[geo]>=0.1,<0.2' matplotlib\n"
    "\n"
    "import os\n"
    "import sondio\n"
    "\n"
    "sondio.api_key = os.environ.get(\"SONDIO_API_KEY\", \"sk_sondio_your_key_here\")\n"
    "print(f\"sondio {sondio.__version__}\")"
)


def ghg_facility_heatmap() -> nbf.NotebookNode:
    cells = [
        _md(
            "# GHG facility emissions by state (choropleth)\n"
            "\n"
            "Aggregate EPA GHGRP facility-level CO₂e emissions to the state level "
            "and render a simple choropleth on top of `sondio.geo.subdivisions` "
            "polygons. Requires the `sondio[geo]` extra."
        ),
        _code(SETUP_CELL),
        _code(
            "# All reporting facilities, latest year the API returns. Paginate — the\n"
            "# dataset is ~8k facilities, well within the free-tier page cap.\n"
            "fac = sondio.us.ghg.facilities(all_pages=True)\n"
            "print(f\"{len(fac)} facilities\")\n"
            "fac.head()"
        ),
        _code(
            "# Aggregate CO2e by state.\n"
            "by_state = (\n"
            "    fac.dropna(subset=[\"state\", \"total_co2e\"])\n"
            "       .groupby(\"state\", as_index=False)[\"total_co2e\"].sum()\n"
            "       .rename(columns={\"total_co2e\": \"co2e_tons\"})\n"
            "       .sort_values(\"co2e_tons\", ascending=False)\n"
            ")\n"
            "by_state.head(10)"
        ),
        _code(
            "# Fetch state polygons (GeoDataFrame, EPSG:4326).\n"
            "states = sondio.geo.subdivisions(country=\"US\", with_geometry=True)\n"
            "print(f\"{len(states)} subdivisions\")\n"
            "states.head()"
        ),
        _code(
            "# Merge emissions onto the polygons via local_code (e.g. 'TX').\n"
            "states = states.merge(by_state, left_on=\"local_code\", right_on=\"state\", how=\"left\")\n"
            "states[\"co2e_tons\"] = states[\"co2e_tons\"].fillna(0)\n"
            "states[[\"local_code\", \"name\", \"co2e_tons\"]].sort_values(\"co2e_tons\", ascending=False).head(10)"
        ),
        _code(
            "import matplotlib.pyplot as plt\n"
            "\n"
            "# Clip to CONUS so Alaska doesn't dominate the frame.\n"
            "conus = states.loc[~states[\"local_code\"].isin([\"AK\", \"HI\", \"PR\", \"VI\", \"GU\", \"AS\", \"MP\"])]\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(10, 6))\n"
            "conus.plot(\n"
            "    column=\"co2e_tons\", ax=ax, cmap=\"OrRd\",\n"
            "    legend=True, legend_kwds={\"label\": \"CO2e (metric tons)\", \"shrink\": 0.6},\n"
            "    edgecolor=\"#555\", linewidth=0.4,\n"
            ")\n"
            "ax.set_axis_off()\n"
            "ax.set_title(\"EPA GHGRP reported CO2e by state (CONUS)\")\n"
            "plt.show()"
        ),
        _md(
            "## Next steps\n"
            "- Filter by `industry_type` (e.g. power plants, oil & gas production).\n"
            "- Swap the aggregate for `mean` or `count(facility_id)` to study intensity.\n"
            "- Clip to a single state and overlay well locations for a cross-vertical view."
        ),
    ]
    return _nb(cells)


def pipeline_safety_explorer() -> nbf.NotebookNode:
    cells = [
        _md(
            "# Pipeline safety explorer — incidents by state\n"
            "\n"
            "PHMSA pipeline incidents aggregated by state, with a simple bar chart "
            "and a cross-reference to nearby oil & gas wells for context."
        ),
        _code(SETUP_CELL),
        _code(
            "# Past several years of reported incidents.\n"
            "incidents = sondio.us.phmsa.pipeline_incidents(all_pages=True)\n"
            "print(f\"{len(incidents)} incidents\")\n"
            "incidents.head()"
        ),
        _code(
            "summary = (\n"
            "    incidents.groupby(\"state\", dropna=True)\n"
            "             .agg(count=(\"id\", \"size\"),\n"
            "                  injuries=(\"injuries\", \"sum\"),\n"
            "                  fatalities=(\"fatalities\", \"sum\"),\n"
            "                  property_damage=(\"property_damage\", \"sum\"))\n"
            "             .sort_values(\"count\", ascending=False)\n"
            "             .head(15)\n"
            ")\n"
            "summary"
        ),
        _code(
            "import matplotlib.pyplot as plt\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 5))\n"
            "summary[\"count\"].plot(kind=\"bar\", ax=ax, color=\"#6a8caf\")\n"
            "ax.set_ylabel(\"incidents\")\n"
            "ax.set_xlabel(\"state\")\n"
            "ax.set_title(\"PHMSA pipeline incidents — top 15 states\")\n"
            "plt.tight_layout(); plt.show()"
        ),
        _code(
            "# Drill into one state: Texas.\n"
            "tx = incidents.loc[incidents[\"state\"] == \"TX\"].copy()\n"
            "tx = tx.dropna(subset=[\"latitude\", \"longitude\"])\n"
            "print(f\"{len(tx)} TX incidents with coordinates\")\n"
            "tx[[\"incident_date\", \"operator_name\", \"city\", \"cause\", \"property_damage\"]].head(10)"
        ),
        _md(
            "## Next steps\n"
            "- Filter by `cause` to isolate corrosion vs excavation damage.\n"
            "- Join with `sondio.oilgas.wells(state=\"TX\")` to cluster incidents near producing assets.\n"
            "- Compare against `sondio.earthquakes(state=\"TX\")` to surface seismic-adjacent ruptures."
        ),
    ]
    return _nb(cells)


def aquifer_exemptions_near_population() -> nbf.NotebookNode:
    cells = [
        _md(
            "# EPA UIC aquifer exemptions — Texas overview\n"
            "\n"
            "Visualize EPA Underground Injection Control (UIC) aquifer exemptions in "
            "Texas, ranked by injection-zone depth. Useful as a quick audit of "
            "where the groundwater-protection exclusions are concentrated."
        ),
        _code(SETUP_CELL),
        _code(
            "ae = sondio.us.epa.aquifer_exemptions(state=\"TX\", all_pages=True)\n"
            "print(f\"{len(ae)} exemptions\")\n"
            "ae.head()"
        ),
        _code(
            "# Shallowest exemptions are the most scrutinized — a few hundred feet.\n"
            "shallow = ae.dropna(subset=[\"depth_ft\"]).sort_values(\"depth_ft\").head(20)\n"
            "shallow[[\"well_class\", \"county\", \"injection_zone\", \"depth_ft\", \"latitude\", \"longitude\"]]"
        ),
        _code(
            "# County rollup — where do the exemptions cluster?\n"
            "by_county = (\n"
            "    ae.dropna(subset=[\"county\"])\n"
            "      .groupby(\"county\").size().sort_values(ascending=False).head(15)\n"
            ")\n"
            "by_county"
        ),
        _code(
            "import matplotlib.pyplot as plt\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 6))\n"
            "pts = ae.dropna(subset=[\"latitude\", \"longitude\"])\n"
            "ax.scatter(pts[\"longitude\"], pts[\"latitude\"], s=6, c=pts[\"depth_ft\"], cmap=\"viridis\", alpha=0.7)\n"
            "ax.set_title(\"Texas UIC aquifer exemptions (color = depth_ft)\")\n"
            "ax.set_xlabel(\"longitude\"); ax.set_ylabel(\"latitude\")\n"
            "plt.show()"
        ),
        _md(
            "## Next steps\n"
            "- Overlay with `sondio.geo.subdivisions(country=\"US\", with_geometry=True)` for a true choropleth.\n"
            "- Cross-reference with `sondio.us.epa.impaired_waters(state=\"TX\")` to flag collocations.\n"
            "- Add `well_class=\"II\"` to isolate oil & gas UIC wells specifically."
        ),
    ]
    return _nb(cells)


def getting_started() -> nbf.NotebookNode:
    cells = [
        _md(
            "# Getting Started with Sondio\n"
            "\n"
            "Install the SDK, plug in your API key, and run your first query — all "
            "in under a minute."
        ),
        _md(
            "## 1. Install\n"
            "\n"
            "```bash\n"
            "pip install sondio           # core (DataFrames only)\n"
            "pip install 'sondio[geo]'    # adds GeoDataFrame support\n"
            "```"
        ),
        _md(
            "## 2. Set your API key\n"
            "\n"
            "Grab one at [sondio.io/developers](https://sondio.io/developers). "
            "Then set it however you like — in-notebook, via environment variable, "
            "or in `~/.sondio/config`."
        ),
        _code(
            "import os\n"
            "import sondio\n"
            "\n"
            "sondio.api_key = os.environ.get(\"SONDIO_API_KEY\", \"sk_sondio_your_key_here\")\n"
            "print(f\"sondio {sondio.__version__}\")"
        ),
        _md(
            "## 3. Your first query\n"
            "\n"
            "Every call returns a pandas DataFrame. Here are recent magnitude-3+ "
            "earthquakes in Texas:"
        ),
        _code(
            "quakes = sondio.earthquakes(state=\"TX\", min_mag=3.0, days=90, limit=20, page=1)\n"
            "quakes.head()"
        ),
        _md(
            "Pagination is opt-in. The line above fetched page 1 only — pass "
            "`all_pages=True` to iterate or `page=N` for a specific page."
        ),
        _md(
            "## 4. Other namespaces\n"
            "\n"
            "The SDK mirrors the Sondio [naming convention](https://github.com/sondio-io/sondio/blob/main/docs/reference/dataset-naming.md):\n"
            "\n"
            "| Call | Dataset |\n"
            "|------|---------|\n"
            "| `sondio.oilgas.wells(country=\"US\", state=\"TX\")` | Oil & gas wells |\n"
            "| `sondio.oilgas.permits(state=\"TX\")` | Drilling permits |\n"
            "| `sondio.us.ghg.facilities(state=\"TX\")` | EPA GHGRP facilities |\n"
            "| `sondio.us.npdes.permits(state=\"TX\")` | Clean Water Act permits |\n"
            "| `sondio.us.phmsa.pipeline_incidents(state=\"TX\")` | Pipeline incidents |\n"
            "| `sondio.us.epa.aquifer_exemptions(state=\"TX\")` | UIC aquifer exemptions |\n"
            "| `sondio.earthquakes(state=\"TX\")` | USGS earthquakes |\n"
            "| `sondio.geo.subdivisions(country=\"US\")` | States / provinces |"
        ),
        _code(
            "facs = sondio.us.ghg.facilities(state=\"TX\", limit=10, page=1)\n"
            "facs[[\"facility_name\", \"city\", \"industry_type\", \"total_co2e\"]].sort_values(\"total_co2e\", ascending=False)"
        ),
        _md(
            "## 5. Where to go next\n"
            "\n"
            "- **Gallery:** [sondio-io/sondio-notebooks](https://github.com/sondio-io/sondio-notebooks) — one notebook per dataset.\n"
            "- **Docs:** [sondio.io/developers](https://sondio.io/developers)\n"
            "- **API reference:** [api.sondio.io](https://api.sondio.io)"
        ),
    ]
    return _nb(cells)


def main() -> None:
    outputs = {
        REPO_ROOT / "env" / "ghg-facility-heatmap.ipynb": ghg_facility_heatmap(),
        REPO_ROOT / "cross-vertical" / "pipeline-safety-explorer.ipynb": pipeline_safety_explorer(),
        REPO_ROOT / "env" / "aquifer-exemptions-near-population.ipynb": aquifer_exemptions_near_population(),
    }
    for path, nb in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            nbf.write(nb, f)
        print(f"wrote {path.relative_to(REPO_ROOT)}")

    # Getting-started lives in the SDK repo so it ships with the package.
    sdk_examples = REPO_ROOT.parent / "sondio-python" / "examples"
    if sdk_examples.exists():
        gs_path = sdk_examples / "01-getting-started.ipynb"
        with gs_path.open("w", encoding="utf-8") as f:
            nbf.write(getting_started(), f)
        print(f"wrote {gs_path}")
    else:
        print(f"(skipped getting-started — {sdk_examples} not found)")


if __name__ == "__main__":
    main()
