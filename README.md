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

The key idea is transparency: you see the full flow from **CSV → Pandas → Flask routes → JSON → browser → DOM/SVG**, and you can extend the dashboard by editing a simple **YAML config file** instead of rewriting core code.

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
- **Sample dataset** (`data/sample_sales.csv`) with realistic sales data.
- **JSON API** endpoints for metrics, charts, and config.
- **Vanilla JS frontend** that:
  - Fetches JSON from Flask
  - Renders KPI cards and a table
  - Draws bar and line charts using SVG
  - Reacts to filter changes (date range)
- **Production-minded**:
  - Clean project structure
  - Example Dockerfile
  - Gunicorn command for deployment
- **Easy to extend**: add new metrics or charts by editing the config file.

---

## Project Structure

```text
create-an-interactive-data-dashboard-with-python/
├── app.py                         # Simple entrypoint using the Flask app factory
├── app/
│   ├── __init__.py                # App factory, config loading, blueprint registration
│   ├── config_loader.py           # Load and validate dashboard config (YAML)
│   ├── data.py                    # Pandas data loading and aggregation helpers
│   └── routes.py                  # HTML view + JSON API endpoints
├── config/
│   └── dashboard.yml              # Config describing metrics, charts, and filters
├── data/
│   └── sample_sales.csv           # Small sample dataset for the dashboard
├── static/
│   ├── css/
│   │   └── styles.css             # Basic responsive dashboard styling
│   └── js/
│       └── dashboard.js           # Vanilla JS for fetching data and rendering UI + charts
├── templates/
│   ├── base.html                  # Base HTML layout
│   └── dashboard.html             # Dashboard page template
├── tests/
│   └── test_api.py                # Minimal tests for JSON API endpoints
├── .env.example                   # Example environment variables
├── Dockerfile                     # Simple Docker image for deployment
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation and quickstart
```

---

## How It Works

High-level data flow:

```text
CSV (data/sample_sales.csv)
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
   Browser fetch() calls (static/js/dashboard.js)
        │
        ▼
   DOM + SVG updates (cards, table, bar/line charts)
```

- On startup, the app:
  - Loads `config/dashboard.yml`.
  - Loads `data/sample_sales.csv` into a Pandas DataFrame.
- API endpoints use the config to compute metrics and chart data.
- The frontend fetches `/api/config`, `/api/metrics`, and `/api/charts/<id>` and renders the UI dynamically.
- Filters (e.g., date range) are passed as query parameters to the API and applied in Pandas.

---

## Installation

### Prerequisites

- Python **3.10+**
- Git

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

# Copy environment example (optional)
cp .env.example .env
```

By default, the app will use `config/dashboard.yml` and `data/sample_sales.csv`.

---

## Quick Start: Run the Dashboard Locally

From the project root:

```bash
# Ensure your virtualenv is active
source .venv/bin/activate  # or Windows equivalent

# Run the app
python app.py
```

Then open:

- http://127.0.0.1:5000

You should see a simple dashboard with:

- KPI cards (e.g., Total Revenue, Total Units Sold)
- A line chart of revenue over time
- A bar chart of revenue by region
- A table of recent rows
- A date range filter that updates the metrics and charts

---

## Usage Details

### Environment variables

The app reads a few optional environment variables (see `.env.example`):

- `FLASK_ENV`: `development` or `production` (defaults to `development`).
- `FLASK_DEBUG`: `1` or `0` (defaults to `1` in development).
- `DASHBOARD_CONFIG_PATH`: override path to the dashboard config file.
- `DASHBOARD_DATA_PATH`: override path to the CSV data file.

You can set them in a `.env` file (if you use `python-dotenv`) or via your shell/hosting provider.

---

## Configuration: `config/dashboard.yml`

The dashboard is driven by a YAML config file. The default `config/dashboard.yml` looks like this (simplified):

```yaml
# config/dashboard.yml

data_source: data/sample_sales.csv

date_column: date

metrics:
  - id: total_revenue
    label: Total Revenue
    column: revenue
    aggregation: sum
    format: "$,.2f"

  - id: total_units
    label: Total Units Sold
    column: units_sold
    aggregation: sum
    format: ",d"

  - id: avg_order_value
    label: Avg Order Value
    numerator: revenue
    denominator: units_sold
    aggregation: ratio
    format: "$,.2f"

charts:
  - id: revenue_over_time
    label: Revenue Over Time
    type: line
    x: date
    y: revenue
    aggregation: sum

  - id: revenue_by_region
    label: Revenue by Region
    type: bar
    x: region
    y: revenue
    aggregation: sum

filters:
  - id: date_range
    type: date_range
    label: Date Range
    column: date
```

### Adding a new metric (card)

1. Open `config/dashboard.yml`.
2. Add a new entry under `metrics`, for example:

```yaml
  - id: orders_count
    label: Number of Orders
    column: order_id
    aggregation: nunique
    format: ",d"
```

3. Restart the app (`python app.py`).
4. The new KPI card will appear automatically on the dashboard.

### Adding a new chart

1. Add a new chart definition under `charts`, for example:

```yaml
  - id: units_by_product
    label: Units Sold by Product
    type: bar
    x: product
    y: units_sold
    aggregation: sum
```

2. Restart the app.
3. The frontend will fetch `/api/charts/units_by_product` and render a new bar chart.

The frontend is generic: it reads the config from `/api/config` and creates containers for each metric and chart, so you rarely need to touch `dashboard.js` when adding new items.

---

## Backend: Flask + Pandas

Key modules:

- `app/__init__.py`: creates the Flask app, loads config, and registers routes.
- `app/config_loader.py`: loads and validates `dashboard.yml`.
- `app/data.py`: loads the CSV into a Pandas DataFrame and exposes helper functions to compute metrics and chart data.
- `app/routes.py`: defines routes:
  - `/` → HTML dashboard page
  - `/api/config` → dashboard config (for the frontend)
  - `/api/metrics` → KPI metrics JSON
  - `/api/charts/<chart_id>` → chart data JSON

Example: using the data helpers in Python code:

```python
from app.data import load_data, compute_metrics
from app.config_loader import load_dashboard_config

config = load_dashboard_config("config/dashboard.yml")
df = load_data(config)

metrics = compute_metrics(df, config["metrics"], filters={})
for metric in metrics:
    print(metric["id"], metric["value"])
```

---

## Frontend: HTML, CSS, and Vanilla JavaScript

Templates:

- `templates/base.html`: base layout and asset includes.
- `templates/dashboard.html`: dashboard content area.

Static assets:

- `static/css/styles.css`: simple responsive layout for header, filters, cards, charts, and table.
- `static/js/dashboard.js`: main JS entrypoint.

`dashboard.js` does the following:

1. On page load, fetches `/api/config` to know which metrics and charts to render.
2. Builds the filter UI (date range inputs) based on config.
3. Fetches `/api/metrics` and `/api/charts/<id>` with current filters.
4. Renders:
   - KPI cards as simple `<div>` elements.
   - A table of recent rows.
   - A **line chart** and **bar chart** using SVG elements created with `document.createElementNS`.
5. Listens for filter changes and re-fetches data.

Because everything is vanilla JS, you can inspect and tweak the chart drawing logic directly.

---

## API Endpoints

All endpoints are defined in `app/routes.py`.

- `GET /`
  - Renders the main dashboard page.

- `GET /api/config`
  - Returns the parsed dashboard config (minus internal fields).

- `GET /api/metrics?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
  - Returns a JSON object like:

```json
{
  "metrics": [
    {"id": "total_revenue", "label": "Total Revenue", "value": 12345.67, "formatted": "$12,345.67"},
    {"id": "total_units", "label": "Total Units Sold", "value": 987, "formatted": "987"}
  ]
}
```

- `GET /api/charts/<chart_id>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
  - Returns chart data like:

```json
{
  "id": "revenue_over_time",
  "label": "Revenue Over Time",
  "type": "line",
  "points": [
    {"x": "2024-01-01", "y": 1234.5},
    {"x": "2024-01-02", "y": 2345.6}
  ]
}
```

The frontend uses these shapes to render charts.

---

## Running Tests

This repo includes a minimal test to sanity-check the API.

From the project root:

```bash
pip install -r requirements.txt  # if not already installed
pytest
```

`tests/test_api.py` will:

- Create a test client
- Hit `/api/metrics` and `/api/charts/revenue_over_time`
- Assert that the responses are 200 and contain expected keys

---

## Deployment

### Gunicorn (recommended for production)

Once your app is working locally, you can run it with Gunicorn:

```bash
pip install gunicorn

# From the project root
gunicorn "app:create_app()" --bind 0.0.0.0:8000
```

Then visit `http://localhost:8000`.

### Docker

A simple `Dockerfile` is included.

Build and run:

```bash
docker build -t flask-dashboard .
docker run -p 8000:8000 flask-dashboard
```

This will run the app with Gunicorn inside the container, listening on port 8000.

### PaaS (Render, Railway, etc.)

Most PaaS providers can run a Gunicorn-based Flask app. Typical steps:

1. Push this repo to your own GitHub account.
2. Create a new web service on your PaaS.
3. Set the start command to something like:

   ```bash
   gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
   ```

4. Set environment variables (if needed) for `DASHBOARD_CONFIG_PATH` and `DASHBOARD_DATA_PATH`.

---

## Extending the Dashboard

Here are some concrete ways to extend this baseline:

1. **Swap the dataset**
   - Replace `data/sample_sales.csv` with your own CSV.
   - Update `data_source` and `date_column` in `config/dashboard.yml`.
   - Adjust metrics and charts to match your column names.

2. **Add new metrics and charts**
   - Add entries under `metrics` and `charts` in `config/dashboard.yml`.
   - Restart the app; the frontend will adapt automatically.

3. **Connect to a database**
   - Modify `app/data.py` to load data from a database instead of CSV.
   - Keep the same interface (`load_data`, `compute_metrics`, `compute_chart_data`) so the rest of the app doesn’t change.

4. **Add authentication**
   - Wrap the `/` route and API routes with your preferred auth (Flask-Login, simple token check, reverse proxy auth, etc.).

5. **Improve UI/UX**
   - Enhance `static/css/styles.css` with your branding.
   - Add more interactive elements in `static/js/dashboard.js` (tooltips, hover states, etc.).

---

## Roadmap / Possible Extensions

- Add support for more chart types (stacked bar, area) using the same SVG primitives.
- Implement server-side caching for expensive aggregations.
- Add pagination and sorting to the data table.
- Provide an example of loading data from a SQL database.
- Add a small CLI to generate a new dashboard project from this template.

---

## PLEX & Medium

This repo is explained in more detail in the PLEX article:

> https://plexdata.online/post/create-an-interactive-data-dashboard-with-python-from-zero-to-deployed-in-minutes

You can also follow Dorian’s broader writing on Medium:

> https://medium.com/@doriansotpyrc

Both the article and this repo are designed to be used together: read the article for the narrative and reasoning, and use this repo as a ready-made starting point for your own internal dashboards.

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file if present, or treat this notice as granting MIT terms.
