
# Create an Interactive Data Dashboard with Python: From Zero to Deployed in Minutes

A minimal, configurable Flask + Pandas + vanilla JavaScript dashboard starter kit. Load a CSV, expose a JSON API, and render KPI cards and charts in the browser — no Plotly, no Streamlit, no heavy charting libraries.

This repo backs the PLEX tutorial **“Create an Interactive Data Dashboard with Python: From Zero to Deployed in Minutes”** and is designed so you can clone, run, and extend a real dashboard in minutes.

---

## Overview

This project shows how to build an interactive data dashboard from scratch using:

- **Flask** for the web server and JSON API
- **Pandas** for data loading and aggregation
- **HTML/CSS** for layout and styling
- **Vanilla JavaScript + SVG** for interactive charts (no charting frameworks)

The key idea is transparency: you see the full flow from

> **CSV → Pandas → Flask routes → JSON → browser → DOM/SVG**

and you can extend the dashboard by editing a simple **YAML config file** instead of rewriting core code.

For a deeper walkthrough, see the PLEX article:

> https://plexdata.online/post/create-an-interactive-data-dashboard-with-python-from-zero-to-deployed-in-minutes

You can also follow Dorian’s broader writing on Medium:

> https://medium.com/@doriansotpyrc

---

## Features

- **Minimal stack**: Flask + Pandas + standard library + vanilla JS (no Plotly/Streamlit/Dash).
- **Config-driven dashboard** via `config/dashboard.yml`:
  - Define metrics (KPI cards)
  - Define charts (bar/line) and their data sources
  - Define simple filters (e.g., date range)
- **Sample datasets** in `data/`:
  - `sample_sales.csv` (baseline sales example)
  - `marketing_campaign_performance.csv` (marketing campaign example)
- **JSON API** endpoints for metrics, charts, and table rows.
- **Vanilla JS frontend** that:
  - Fetches JSON from Flask
  - Renders KPI cards and a table
  - Draws bar and line charts using SVG
  - Reacts to filter changes (date range)
- **Production-minded**:
  - Clean project structure
  - Example Dockerfile
  - Gunicorn command for deployment
- **Easy to extend**: add new metrics, charts, or datasets by editing config.

---

## Project Structure

```text
create-an-interactive-data-dashboard-with-python/
├── app.py                         # Simple entrypoint using the Flask app factory
├── app/
│   ├── __init__.py                # App factory, config loading, blueprint registration
│   ├── config_loader.py           # Load and validate dashboard config (YAML)
│   ├── data.py                    # Pandas data loading and aggregation helpers
│   ├── routes.py                  # HTML view + JSON API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css         # PLEX-style dashboard layout and theming
│   │   └── js/
│   │       └── dashboard.js       # Vanilla JS for fetching data and rendering UI + charts
│   └── templates/
│       ├── base.html              # Base HTML layout + header/footer
│       └── dashboard.html         # Dashboard page template
├── config/
│   └── dashboard.yml              # Config describing data source, metrics, charts, filters
├── data/
│   ├── sample_sales.csv           # Original sales dataset
│   └── marketing_campaign_performance.csv  # Marketing campaign dataset
├── tests/
│   └── test_api.py                # Minimal tests for JSON API endpoints
├── Dockerfile                     # Simple Docker image for deployment
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation and quickstart
````

---

## How It Works

High-level data flow:

```text
CSV (data/*.csv)
        │
        ▼
   Pandas DataFrame  (app/data.py)
        │
        ▼
   Aggregations & KPIs (driven by config/dashboard.yml)
        │
        ▼
   Flask JSON API (app/routes.py)
        │
        ▼
   Browser fetch() calls (app/static/js/dashboard.js)
        │
        ▼
   DOM + SVG updates (cards, table, bar/line charts)
```

On startup, the app:

1. Loads `config/dashboard.yml`.
2. Loads the CSV defined by `data_source` into a Pandas DataFrame.
3. Stores both the config and the DataFrame in `app.config`.

API endpoints then:

* Apply any filters (e.g. date range).
* Compute metrics and chart series.
* Return JSON the frontend can render.

---

## Installation

### Prerequisites

* Python **3.10+**
* Git

Optional (for deployment): Docker, Gunicorn.

### Clone and set up

```bash
git clone git@github-dorian:dorian-sotpyrc/create-an-interactive-data-dashboard-with-python.git
cd create-an-interactive-data-dashboard-with-python

# (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

By default, the app will use `config/dashboard.yml` and whatever `data_source` you configure there.

---

## Quick Start: Run the Dashboard Locally

From the project root:

```bash
# Ensure your virtualenv is active
source .venv/bin/activate  # or Windows equivalent

# Run the app
python app.py
```

By default this starts a development server on:

* [http://127.0.0.1:8509](http://127.0.0.1:8509)

(or `http://<your-server-ip>:8509` if you’re running on a remote box).

You should see a dashboard with:

* KPI cards
* Line and bar charts
* A “Recent rows” table
* A date range filter that updates metrics and charts

---

## Configuration: `config/dashboard.yml`

The dashboard is driven by a YAML config file. At the top you choose the dataset:

```yaml
# Path to the CSV data source (relative to project root)
data_source: data/sample_sales.csv

# Name of the date column in the CSV (used for filtering and time series)
date_column: date
```

Below that you define:

* **metrics** → KPI cards
* **charts**  → bar/line charts
* **filters** → currently a date range

Example (simplified):

```yaml
metrics:
  - id: total_revenue
    label: Total Revenue
    column: revenue
    aggregation: sum
    format: "$,.2f"

charts:
  - id: revenue_over_time
    label: Revenue Over Time
    type: line
    x: date
    y: revenue
    aggregation: sum

filters:
  - id: date_range
    type: date_range
    label: Date Range
    column: date
```

### Metric `format` mini-DSL

Metric values can be formatted using a small set of patterns. In `app/data.py`, `_format_value` supports:

* `",d"` → integer with thousands separators

  * Example: `12345` → `12,345`
* `"$,.2f"` → currency with thousands separators and 2 decimals

  * Example: `12345.6` → `$12,345.60`
* `"0.0"` / `"0.00"` → plain decimals

  * Example: `9.1995` + `"0.0"` → `9.2`
* `"0.0x"` / `"0.00x"` → multiplier

  * Example: `3.27` + `"0.0x"` → `3.3x`
* `"0.0%"` / `"0.00%"` → percentage (value is a ratio)

  * Example: `0.1331` + `"0.0%"` → `13.3%`
* Any unsupported pattern falls back to `str(value)`.

If a value is `NaN` or `inf`, it will be rendered as `"-"` to avoid ugly output or crashes.

---

## How to Load a New Dataset (Step-by-Step)

This is the key part of the tutorial: you should be able to swap datasets and reconfigure the dashboard without touching Python or JS.

### 1. Drop your CSV into `data/`

Example: we added a marketing dataset:

```text
data/
├── sample_sales.csv
└── marketing_campaign_performance.csv
```

`marketing_campaign_performance.csv` looks like:

```csv
date,campaign,channel,spend,clicks,signups,revenue
2025-01-01,Launch A,Search,420,950,120,3100
2025-01-01,Launch A,Social,260,780,90,2100
...
```

### 2. Point the config at the new file

In `config/dashboard.yml`, update `data_source`:

```yaml
# OLD:
# data_source: data/sample_sales.csv

# NEW:
data_source: data/marketing_campaign_performance.csv

# Date column stays the same name in this dataset
date_column: date
```

### 3. Update metrics to match new columns

**Previous (sales) metrics**:

```yaml
# metrics:
#   - id: total_revenue
#     label: Total Revenue
#     column: revenue
#     aggregation: sum
#     format: "$,.2f"
#
#   - id: total_units
#     label: Total Units Sold
#     column: units_sold
#     aggregation: sum
#     format: ",d"
#
#   - id: avg_order_value
#     label: Avg Order Value
#     numerator: revenue
#     denominator: units_sold
#     aggregation: ratio
#     format: "$,.2f"
```

**New (marketing) metrics**:

```yaml
metrics:
  - id: total_spend
    label: Total Spend
    column: spend
    aggregation: sum
    format: "$,.2f"

  - id: total_revenue
    label: Total Revenue
    column: revenue
    aggregation: sum
    format: "$,.2f"

  - id: total_signups
    label: Total Signups
    column: signups
    aggregation: sum
    format: ",d"

  - id: roas
    label: ROAS (Revenue / Spend)
    numerator: revenue
    denominator: spend
    aggregation: ratio
    format: "0.0x"      # e.g. 9.2x

  - id: conversion_rate
    label: Conversion Rate (Signups / Clicks)
    numerator: signups
    denominator: clicks
    aggregation: ratio
    format: "0.0%"      # e.g. 13.3%
```

> Tip: if you hit a `KeyError` in the logs, it usually means the `column`, `numerator`, or `denominator` name in YAML doesn’t exist in your CSV. Double-check spelling and case.

### 4. Update charts to use the new schema

**Previous charts**:

```yaml
# charts:
#   - id: revenue_over_time
#     label: Revenue Over Time
#     type: line
#     x: date
#     y: revenue
#     aggregation: sum
#
#   - id: revenue_by_region
#     label: Revenue by Region
#     type: bar
#     x: region
#     y: revenue
#     aggregation: sum
```

**New marketing charts**:

```yaml
charts:
  - id: revenue_over_time
    label: Revenue Over Time
    type: line
    x: date
    y: revenue
    aggregation: sum

  - id: spend_over_time
    label: Spend Over Time
    type: line
    x: date
    y: spend
    aggregation: sum

  - id: revenue_by_channel
    label: Revenue by Channel
    type: bar
    x: channel
    y: revenue
    aggregation: sum

  - id: signups_by_campaign
    label: Signups by Campaign
    type: bar
    x: campaign
    y: signups
    aggregation: sum
```

The frontend reads this config from `/api/config`, creates one card per metric and one container per chart, and then calls the corresponding `/api/charts/<id>` endpoints. No JS changes required.

### 5. Restart the app

Whenever you change `dashboard.yml`:

```bash
python app.py
```

Refresh the browser; you should see the new KPIs and charts wired to your new dataset.

---

## How to Rename the Dashboard (Title, Subtitle, Branding)

You can rename the project and tweak the UI copy without touching any Python.

### 1. Change the HTML `<title>`

Edit `app/templates/base.html` and look for the `<title>` tag:

```html
<head>
  <title>FLASK + PANDAS DASHBOARD</title>
  ...
</head>
```

Replace it with your own title, for example:

```html
<title>Marketing Performance Dashboard · Flask + Pandas</title>
```

This controls the browser tab text and search snippet title.

### 2. Update the header text

In the same file (or in `dashboard.html`, depending on how you structured it), you’ll see something like:

```html
<header class="app-header">
  <div class="app-header-inner">
    <h1 class="app-title">FLASK + PANDAS DASHBOARD</h1>
    <p class="app-subtitle">Interactive dashboard with vanilla JS charts</p>
  </div>
</header>
```

Update the copy:

```html
<h1 class="app-title">Marketing Performance Dashboard</h1>
<p class="app-subtitle">
  Track spend, revenue, and signups across campaigns with a pure Flask + Pandas stack.
</p>
```

These strings are purely presentational; no backend code depends on them.

### 3. (Optional) Tweak the styling to match your brand

All layout and colours live in:

* `app/static/css/styles.css`

The palette is defined at the top as CSS variables:

```css
:root {
  --lavender: #E3E3ED;
  --atomic-tangerine: #EC793F;
  --sandy-brown: #F2A066;
  --sunlit-clay: #EAB467;
  --soft-periwinkle: #A690F9;
  --bright-lavender: #BA80E2;
  --deep-lilac: #6F45BC;
  ...
}
```

You can adjust these values or override specific components (cards, charts, header) to match your project’s look and feel.

---

## Backend: Flask + Pandas

Key modules:

* `app/__init__.py`

  * Creates the Flask app (`create_app()`), loads config and data, registers the blueprint.
* `app/config_loader.py`

  * Loads and validates `config/dashboard.yml`.
* `app/data.py`

  * `load_data(...)` → reads CSV into a DataFrame.
  * `apply_filters(...)` → applies date range filters.
  * `compute_metrics(...)` → calculates KPI metrics based on config.
  * `compute_chart_data(...)` → calculates chart series from config.
* `app/routes.py`

  * `/` → HTML dashboard page
  * `/api/config` → dashboard config (for the frontend)
  * `/api/metrics` → KPI metrics JSON
  * `/api/charts/<chart_id>` → chart data JSON
  * `/api/table` → small “Recent rows” table JSON

You can also import these helpers into your own scripts if you want to reuse the aggregation logic.

---

## Frontend: HTML, CSS, and Vanilla JavaScript

Templates:

* `app/templates/base.html` — shared layout (header, main, footer).
* `app/templates/dashboard.html` — filters, cards, charts, and table.

Static assets:

* `app/static/css/styles.css` — PLEX-style neumorphic dashboard design.
* `app/static/js/dashboard.js` — main JS entrypoint.

`dashboard.js`:

1. Reads `window.DASHBOARD_CONFIG` (injected from Flask).
2. Renders the filter controls (`start_date`, `end_date`, reset).
3. Creates placeholder containers for each chart from the config.
4. Calls:

   * `/api/metrics`
   * `/api/table`
   * `/api/charts/<id>` for each chart
5. Renders:

   * KPI cards (`.card`)
   * Table rows
   * Line and bar charts using SVG primitives

The chart colours and axis styling are set directly in `dashboard.js` and are tuned to match the CSS palette.

---

## API Endpoints

All endpoints are defined in `app/routes.py`.

* `GET /`

  * Renders the main dashboard page.

* `GET /api/config`

  * Returns the parsed dashboard config (minus `data_source`).

* `GET /api/metrics?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

  * Returns:

    ```json
    {
      "metrics": [
        {
          "id": "total_revenue",
          "label": "Total Revenue",
          "value": 45860.0,
          "formatted": "$45,860.00"
        },
        ...
      ]
    }
    ```

* `GET /api/charts/<chart_id>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

  * Returns:

    ```json
    {
      "id": "revenue_over_time",
      "label": "Revenue Over Time",
      "type": "line",
      "points": [
        {"x": "2025-01-01", "y": 7000.0},
        {"x": "2025-01-02", "y": 6900.0}
      ]
    }
    ```

* `GET /api/table?...`

  * Returns up to 50 recent rows as:

    ```json
    {
      "rows": [
        {"date": "2025-01-07", "campaign": "Brand Always-On", ...},
        ...
      ]
    }
    ```

---

## Running Tests

From the project root:

```bash
pip install -r requirements.txt  # if not already installed
pytest
```

`tests/test_api.py` will:

* Create a Flask test client
* Hit `/api/metrics` and `/api/charts/<some_id>`
* Assert that the responses are `200` and contain expected keys

---

## Deployment

### Gunicorn (recommended for production)

```bash
pip install gunicorn

gunicorn "app:create_app()" --bind 0.0.0.0:8000
```

Then visit `http://localhost:8000`.

### Docker

```bash
docker build -t flask-dashboard .
docker run -p 8000:8000 flask-dashboard
```

The Docker image runs Gunicorn inside the container.

### PaaS (Render, Railway, etc.)

1. Push this repo to your GitHub account.

2. Create a new web service.

3. Set the start command to:

   ```bash
   gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
   ```

4. Optionally set environment variables for `DASHBOARD_CONFIG_PATH` and `DASHBOARD_DATA_PATH`.

---

## Extending the Dashboard

Some ideas:

* Swap in your own CSV and build a domain-specific dashboard (finance, IoT, operations, etc.).
* Add more charts (stacked bars, multi-series lines) using the same SVG primitives.
* Plug in a SQL database instead of CSV.
* Add authentication in front of `/` and `/api/*`.
* Add pagination and sorting to the “Recent rows” table.

---

## PLEX & Medium

This repo is explained in more detail in the PLEX article:

> [https://plexdata.online/post/create-an-interactive-data-dashboard-with-python-from-zero-to-deployed-in-minutes](https://plexdata.online/post/create-an-interactive-data-dashboard-with-python-from-zero-to-deployed-in-minutes)

You can also follow Dorian’s broader writing on Medium:

> [https://medium.com/@doriansotpyrc](https://medium.com/@doriansotpyrc)

Both the article and this repo are designed to be used together: read the article for the narrative and reasoning, and use this repo as a ready-made starting point for your own internal dashboards.

---

## License

This project is licensed under the **MIT License**. Treat this notice as granting MIT terms if a separate `LICENSE` file is not present.


