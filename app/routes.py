from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, render_template, request

from .data import compute_chart_data, compute_metrics, apply_filters


bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index() -> str:
    """Render the main dashboard page."""
    config = current_app.config["DASHBOARD_CONFIG"]
    return render_template("dashboard.html", config=config)


@bp.route("/api/config")
def api_config():
    """Return the dashboard config for the frontend.

    We return a subset that is safe for the client (no internal paths).
    """
    config = current_app.config["DASHBOARD_CONFIG"].copy()
    # Remove data_source path from client-facing config
    config.pop("data_source", None)
    return jsonify(config)


def _extract_filters() -> Dict[str, Any]:
    return {
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }


@bp.route("/api/metrics")
def api_metrics():
    df = current_app.config["DATAFRAME"]
    config = current_app.config["DASHBOARD_CONFIG"]
    filters = _extract_filters()

    metrics_cfg = config.get("metrics", [])
    metrics = compute_metrics(df, metrics_cfg, filters, config)

    return jsonify({"metrics": metrics})


@bp.route("/api/charts/<chart_id>")
def api_chart(chart_id: str):
    df = current_app.config["DATAFRAME"]
    config = current_app.config["DASHBOARD_CONFIG"]
    filters = _extract_filters()

    chart_cfg = next((c for c in config.get("charts", []) if c.get("id") == chart_id), None)
    if chart_cfg is None:
        return jsonify({"error": f"Unknown chart id: {chart_id}"}), 404

    chart_data = compute_chart_data(df, chart_cfg, filters, config)
    return jsonify(chart_data)


@bp.route("/api/table")
def api_table():
    """Return a small sample of rows for a simple table view."""
    df = current_app.config["DATAFRAME"]
    config = current_app.config["DASHBOARD_CONFIG"]
    filters = _extract_filters()

    filtered = apply_filters(df, config, filters)
    # Return the most recent 50 rows by date if date_column exists
    date_col = config.get("date_column")
    if date_col and date_col in filtered.columns:
        filtered = filtered.sort_values(by=date_col, ascending=False)

    sample = filtered.head(50)
    return jsonify({"rows": sample.to_dict(orient="records")})
