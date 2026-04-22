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
    "%pip install --quiet 'sondio[geo]>=0.1.2,<0.2' matplotlib\n"
    "\n"
    "import sondio\n"
    "# sondio >= 0.1.2 reads your key from Colab Secrets (\U0001f511 sidebar),\n"
    "# Kaggle Secrets, SONDIO_API_KEY env var, or ~/.sondio/config — in that\n"
    "# order. Set whichever fits your environment.\n"
    "print(f\"sondio {sondio.__version__}\")"
)


def earthquake_well_proximity() -> nbf.NotebookNode:
    cells = [
        _md(
            "# Earthquakes near oil & gas wells (Texas)\n"
            "\n"
            "Cross-vertical starter: find oil & gas wells within 20 miles of the "
            "largest recent magnitude 3.0+ earthquake in Texas. Uses a pure-pandas "
            "haversine filter so it runs without any geospatial deps."
        ),
        _code(SETUP_CELL),
        _code(
            "# Strongest recent Texas quake — pull the first page (ordered newest first).\n"
            "quakes = sondio.earthquakes(state=\"TX\", min_mag=3.0, days=365, limit=200, page=1)\n"
            "print(f\"{len(quakes)} earthquakes\")\n"
            "quakes.sort_values(\"magnitude\", ascending=False).head()"
        ),
        _code(
            "# Anchor on the largest quake.\n"
            "focal = quakes.sort_values(\"magnitude\", ascending=False).iloc[0]\n"
            "lat0, lon0 = float(focal[\"latitude\"]), float(focal[\"longitude\"])\n"
            "print(f\"Focal quake: M{focal['magnitude']} on {focal['event_time']} at ({lat0:.3f}, {lon0:.3f})\")"
        ),
        _code(
            "# Pull TX wells, then filter by true distance with haversine.\n"
            "import numpy as np\n"
            "\n"
            "wells = sondio.oilgas.wells(country=\"US\", state=\"TX\", limit=500, all_pages=True)\n"
            "wells = wells.dropna(subset=[\"latitude\", \"longitude\"]).copy()\n"
            "print(f\"{len(wells)} TX wells\")"
        ),
        _code(
            "def haversine_miles(lat1, lon1, lat2, lon2):\n"
            "    R = 3958.8\n"
            "    phi1, phi2 = np.radians(lat1), np.radians(lat2)\n"
            "    dphi = np.radians(lat2 - lat1)\n"
            "    dlam = np.radians(lon2 - lon1)\n"
            "    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam/2)**2\n"
            "    return 2 * R * np.arcsin(np.sqrt(a))\n"
            "\n"
            "wells[\"miles_to_focal\"] = haversine_miles(\n"
            "    lat0, lon0, wells[\"latitude\"].values, wells[\"longitude\"].values\n"
            ")\n"
            "near = wells.loc[wells[\"miles_to_focal\"] <= 20].sort_values(\"miles_to_focal\")\n"
            "print(f\"{len(near)} wells within 20 miles\")\n"
            "near[[\"well_name\", \"operator_name\", \"locality\", \"subdivision\", \"miles_to_focal\"]].head(15)"
        ),
        _code(
            "# Matplotlib scatter — no basemap deps.\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 7))\n"
            "ax.scatter(wells[\"longitude\"], wells[\"latitude\"], s=4, c=\"#aaa\", label=\"TX wells\", alpha=0.5)\n"
            "ax.scatter(near[\"longitude\"], near[\"latitude\"], s=18, c=\"#c44\", label=\"wells < 20 mi\")\n"
            "ax.scatter([lon0], [lat0], s=180, marker=\"*\", c=\"#222\", label=f\"M{focal['magnitude']} quake\")\n"
            "ax.set_xlabel(\"longitude\"); ax.set_ylabel(\"latitude\")\n"
            "ax.set_title(f\"Texas wells near focal earthquake ({focal['event_time']})\")\n"
            "ax.legend(loc=\"upper right\"); ax.grid(alpha=0.2)\n"
            "plt.show()"
        ),
        _md(
            "## Next steps\n"
            "- Widen the window with `days=365 * 3` or drop the state filter for CONUS-wide scope.\n"
            "- Swap `state=\"TX\"` for another seismic region (OK, CA).\n"
            "- Cross with `sondio.us.phmsa.pipeline_incidents(state=\"TX\")` to flag pipelines near the same quake.\n"
            "- Related: [pipeline-safety-explorer](pipeline-safety-explorer.ipynb)."
        ),
    ]
    return _nb(cells)


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


def oilgas_production_trends() -> nbf.NotebookNode:
    cells = [
        _md(
            "# Oil & gas production decline curve\n"
            "\n"
            "Pull the full monthly production history for a long-lived well and plot\n"
            "oil, gas, and water volumes through time. This is the canonical \"decline\n"
            "curve\" landmen and mineral owners look at to understand lease\n"
            "performance and estimate remaining reserves.\n"
            "\n"
            "Uses `sondio.oilgas.production(well_id)`, which resolves at well-level\n"
            "where the source reports per-well volumes, or falls back to the\n"
            "underlying lease where only lease-level data is published."
        ),
        _code(SETUP_CELL),
        _code(
            "# Anchor well: a Kansas oil well (BEREXCO, Butler County) with a long\n"
            "# monthly history. Swap `WELL_ID` for any `external_id` or Sondio UUID —\n"
            "# the API accepts either. Colorado, New Mexico, North Dakota, and\n"
            "# Pennsylvania have the deepest per-well coverage.\n"
            "WELL_ID = \"15-083-21176\"  # BEREXCO LLC — Labette County, KS\n"
            "well_row = sondio.oilgas.wells(search=WELL_ID, limit=1).iloc[0]\n"
            "print(f\"{well_row['well_name']} — {well_row['operator_name']} ({well_row['external_id']})\")\n"
            "well_row[[\"well_name\", \"operator_name\", \"well_type\", \"well_status\", \"locality\", \"subdivision\"]]"
        ),
        _code(
            "# Pull the monthly production history. Default is 24 months; ask for 180\n"
            "# (15 years) to see the full decline curve.\n"
            "prod = sondio.oilgas.production(WELL_ID, months=180)\n"
            "prod = prod.sort_values(\"production_date\").reset_index(drop=True)\n"
            "print(f\"{len(prod)} months of production, earliest {prod['production_date'].min().date()}\")\n"
            "prod.head()"
        ),
        _code(
            "# Three-panel decline curve — oil, gas, water on the same x axis.\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)\n"
            "for ax, col, color, label in zip(\n"
            "    axes,\n"
            "    [\"oil_bbl\", \"gas_mcf\", \"water_bbl\"],\n"
            "    [\"#1a6e3d\", \"#d68b2a\", \"#2a6cad\"],\n"
            "    [\"Oil (bbl/mo)\", \"Gas (mcf/mo)\", \"Water (bbl/mo)\"],\n"
            "):\n"
            "    ax.fill_between(prod[\"production_date\"], 0, prod[col].fillna(0), color=color, alpha=0.6)\n"
            "    ax.plot(prod[\"production_date\"], prod[col].fillna(0), color=color, linewidth=0.8)\n"
            "    ax.set_ylabel(label); ax.grid(alpha=0.2)\n"
            "axes[0].set_title(f\"{well_row['well_name']} — {well_row['operator_name']} ({well_row['external_id']})\")\n"
            "axes[-1].set_xlabel(\"production month\")\n"
            "plt.tight_layout(); plt.show()"
        ),
        _code(
            "# Boe-equivalent lifetime total and peak month.\n"
            "prod[\"boe\"] = prod[\"oil_bbl\"].fillna(0) + prod[\"gas_mcf\"].fillna(0) / 6.0\n"
            "peak = prod.loc[prod[\"boe\"].idxmax()]\n"
            "print(f\"Cumulative BOE: {prod['boe'].sum():,.0f}\")\n"
            "print(f\"Peak month: {peak['production_date'].date()} — {peak['boe']:,.0f} BOE\")"
        ),
        _md(
            "## Next steps\n"
            "- Loop over top-N wells for a single operator and plot combined monthly BOE.\n"
            "- Pass `as_of=` (Pro+ tier) to replay production as it would have looked on a historical date — useful for back-testing acquisition models.\n"
            "- Cross with `sondio.us.phmsa.pipeline_incidents(...)` to flag wells feeding into pipelines with recent incidents.\n"
            "- Related: [earthquake-well-proximity](../cross-vertical/earthquake-well-proximity.ipynb)."
        ),
    ]
    return _nb(cells)


def wind_turbine_density() -> nbf.NotebookNode:
    cells = [
        _md(
            "# US wind fleet — installed capacity + growth trend\n"
            "\n"
            "The US Wind Turbine Database (USWTDB) records every utility-scale\n"
            "turbine in the country — 75k+ units, lat/lon, capacity, year online,\n"
            "make and model. This notebook plots total installed nameplate capacity\n"
            "by state and traces the growth of typical turbine size over time."
        ),
        _code(SETUP_CELL),
        _code(
            "# Full fleet — ~75k rows, ~750 pages at the default page size. Narrow\n"
            "# with `min_year=2010` if you only want modern installs.\n"
            "turbines = sondio.wind_turbines(all_pages=True)\n"
            "print(f\"{len(turbines):,} turbines\")\n"
            "turbines[[\"p_name\", \"t_state\", \"p_year\", \"t_cap\", \"t_manu\", \"t_model\"]].head()"
        ),
        _code(
            "# State totals — installed MW and turbine count. The USWTDB capacity\n"
            "# field t_cap is nameplate kW, so divide by 1000 for MW.\n"
            "state_totals = (\n"
            "    turbines.assign(mw=turbines[\"t_cap\"].fillna(0) / 1000.0)\n"
            "    .groupby(\"t_state\")\n"
            "    .agg(turbines=(\"id\", \"size\"), total_mw=(\"mw\", \"sum\"))\n"
            "    .sort_values(\"total_mw\", ascending=False)\n"
            ")\n"
            "state_totals.head(10)"
        ),
        _code(
            "# Bar chart: top 15 states by installed capacity.\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "top = state_totals.head(15).iloc[::-1]\n"
            "fig, ax = plt.subplots(figsize=(9, 6))\n"
            "ax.barh(top.index, top[\"total_mw\"], color=\"#2a6cad\")\n"
            "ax.set_xlabel(\"Installed capacity (MW)\")\n"
            "ax.set_title(\"US wind fleet — top 15 states by nameplate capacity\")\n"
            "ax.grid(alpha=0.2, axis=\"x\")\n"
            "for y, (state, row) in enumerate(top.iterrows()):\n"
            "    ax.text(row[\"total_mw\"], y, f\"  {int(row['turbines']):,}\", va=\"center\", fontsize=9, color=\"#555\")\n"
            "plt.tight_layout(); plt.show()"
        ),
        _code(
            "# Turbine-size trend: median nameplate capacity by commissioning year.\n"
            "# Newer projects ship bigger rotors — this plots it directly.\n"
            "by_year = (\n"
            "    turbines.dropna(subset=[\"p_year\", \"t_cap\"])\n"
            "    .groupby(\"p_year\")\n"
            "    .agg(median_kw=(\"t_cap\", \"median\"), installs=(\"id\", \"size\"))\n"
            "    .query(\"installs >= 50\")\n"
            ")\n"
            "fig, ax = plt.subplots(figsize=(9, 5))\n"
            "ax.plot(by_year.index, by_year[\"median_kw\"] / 1000.0, marker=\"o\", color=\"#1a6e3d\")\n"
            "ax.set_xlabel(\"commissioning year\"); ax.set_ylabel(\"median nameplate capacity (MW)\")\n"
            "ax.set_title(\"Turbines are getting bigger — median nameplate capacity over time\")\n"
            "ax.grid(alpha=0.2); plt.tight_layout(); plt.show()"
        ),
        _md(
            "## Next steps\n"
            "- Filter with `bbox=(west, south, east, north)` to zoom a single region.\n"
            "- Drill to a specific operator with `project_name=\"Roscoe\"` or `manufacturer=\"GE Wind\"`.\n"
            "- Cross with `sondio.us.phmsa.pipeline_incidents(...)` and `sondio.earthquakes(...)` to build a multi-energy infrastructure map."
        ),
    ]
    return _nb(cells)


def svi_pipeline_incidents() -> nbf.NotebookNode:
    cells = [
        _md(
            "# Environmental justice: pipeline incidents vs social vulnerability\n"
            "\n"
            "Do natural-gas and liquid pipeline incidents cluster in more vulnerable\n"
            "communities? This notebook builds a state-level comparison between\n"
            "PHMSA pipeline incident counts and the CDC Social Vulnerability Index\n"
            "(SVI), then scatters them.\n"
            "\n"
            "Both datasets are public and tracked in Sondio as\n"
            "`sondio.us.phmsa.pipeline_incidents` and `sondio.us.cdc.svi_tracts`."
        ),
        _code(SETUP_CELL),
        _code(
            "# All PHMSA pipeline incidents we have in the dataset (multi-year).\n"
            "incidents = sondio.us.phmsa.pipeline_incidents(all_pages=True)\n"
            "print(f\"{len(incidents):,} incidents\")\n"
            "incidents[[\"operator_name\", \"state\", \"incident_date\", \"total_cost_current\"]].head()"
        ),
        _code(
            "# State-level tract summary: mean RPL (overall social-vulnerability rank,\n"
            "# 0 = least vulnerable, 1 = most) and total population. SVI has ~84k\n"
            "# tracts and we only need the state rollup, so pull the most recent year.\n"
            "import pandas as pd\n"
            "\n"
            "tracts = sondio.us.cdc.svi_tracts(data_year=2022, all_pages=True)\n"
            "print(f\"{len(tracts):,} SVI tracts\")\n"
            "state_svi = (\n"
            "    tracts.dropna(subset=[\"rpl_themes_overall\", \"total_population\"])\n"
            "    .groupby(\"subdivision_code\")\n"
            "    .apply(lambda g: pd.Series({\n"
            "        \"mean_rpl\": (g[\"rpl_themes_overall\"] * g[\"total_population\"]).sum() / g[\"total_population\"].sum(),\n"
            "        \"population\": g[\"total_population\"].sum(),\n"
            "    }))\n"
            ")\n"
            "state_svi.head()"
        ),
        _code(
            "# Incidents per million residents — normalize so small states aren't\n"
            "# drowned out by TX and CA.\n"
            "state_incidents = incidents.groupby(\"state\").size().rename(\"incidents\")\n"
            "state = state_svi.join(state_incidents).dropna()\n"
            "state[\"per_million\"] = state[\"incidents\"] / (state[\"population\"] / 1_000_000)\n"
            "state.sort_values(\"per_million\", ascending=False).head(10)"
        ),
        _code(
            "# Scatter: mean population-weighted SVI vs incidents-per-million.\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(9, 6))\n"
            "ax.scatter(state[\"mean_rpl\"], state[\"per_million\"], s=60, alpha=0.7, color=\"#c44\")\n"
            "for code, row in state.iterrows():\n"
            "    ax.annotate(code, (row[\"mean_rpl\"], row[\"per_million\"]), fontsize=8, xytext=(3, 2), textcoords=\"offset points\")\n"
            "ax.set_xlabel(\"Mean social-vulnerability rank (population-weighted)\")\n"
            "ax.set_ylabel(\"Pipeline incidents per 1M residents\")\n"
            "ax.set_title(\"State-level SVI vs pipeline incidents (PHMSA)\")\n"
            "ax.grid(alpha=0.2); plt.tight_layout(); plt.show()"
        ),
        _md(
            "## Reading the chart\n"
            "\n"
            "Each dot is a state. A state with **higher mean RPL** has, on average,\n"
            "more socially vulnerable census tracts. A state high on the y axis has\n"
            "more pipeline incidents per capita.\n"
            "\n"
            "This rollup is deliberately coarse. A real environmental-justice\n"
            "analysis would join incidents to their containing tract directly — once\n"
            "the incidents table carries lat/lon consistently. The state-level view\n"
            "is the starting point."
        ),
        _md(
            "## Next steps\n"
            "- Narrow to a single vulnerable state (e.g. `state=\"LA\"`) and chart\n"
            "  incident density at the tract level.\n"
            "- Replace the SVI rollup with the `rpl_theme1_socioeconomic` theme if\n"
            "  you care specifically about income + education, not the composite.\n"
            "- Cross with `sondio.oilgas.wells(...)` to show well density in the\n"
            "  same tracts."
        ),
    ]
    return _nb(cells)


def main() -> None:
    outputs = {
        REPO_ROOT / "cross-vertical" / "earthquake-well-proximity.ipynb": earthquake_well_proximity(),
        REPO_ROOT / "env" / "ghg-facility-heatmap.ipynb": ghg_facility_heatmap(),
        REPO_ROOT / "cross-vertical" / "pipeline-safety-explorer.ipynb": pipeline_safety_explorer(),
        REPO_ROOT / "env" / "aquifer-exemptions-near-population.ipynb": aquifer_exemptions_near_population(),
        REPO_ROOT / "energy" / "oilgas-production-trends.ipynb": oilgas_production_trends(),
        REPO_ROOT / "energy" / "wind-turbine-density.ipynb": wind_turbine_density(),
        REPO_ROOT / "cross-vertical" / "svi-pipeline-incidents.ipynb": svi_pipeline_incidents(),
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
