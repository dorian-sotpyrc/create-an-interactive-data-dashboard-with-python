from __future__ import annotations

import os
from typing import Any, Dict, List, Iterable

import pandas as pd


def load_data(path: str, config: Dict[str, Any]) -> pd.DataFrame:
    """Load the CSV data into a Pandas DataFrame.

    The path from the config is resolved relative to the project root if needed.
    """
    # If the path in config is relative, resolve it relative to the project root
    if not os.path.isabs(path):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        path = os.path.join(root_dir, path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found at: {path}")

    df = pd.read_csv(path)

    # Ensure date column is parsed if specified
    date_col = config.get("date_column")
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])

    return df


def apply_filters(df: pd.DataFrame, config: Dict[str, Any], filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply simple filters (currently only date_range) to the DataFrame."""
    result = df.copy()
    date_col = config.get("date_column")

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if date_col and date_col in result.columns and (start_date or end_date):
        if start_date:
            result = result[result[date_col] >= pd.to_datetime(start_date)]
        if end_date:
            result = result[result[date_col] <= pd.to_datetime(end_date)]

    return result


def _format_value(value: float, fmt: str | None) -> str:
    if fmt is None:
        return str(value)
    # Very small formatter supporting a couple of patterns used in config
    if fmt == ",d":
        return f"{int(round(value)):,}"
    if fmt == "$,.2f":
        return f"${value:,.2f}"
    return fmt.format(value) if "{" in fmt else str(value)


def compute_metrics(df: pd.DataFrame, metrics_cfg: Iterable[Dict[str, Any]], filters: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute KPI metrics based on the config.

    Supports aggregations: sum, mean, count, nunique, ratio.
    """
    filtered = apply_filters(df, config, filters)

    results: List[Dict[str, Any]] = []
    for m in metrics_cfg:
        agg = m.get("aggregation", "sum")
        fmt = m.get("format")

        if agg == "ratio":
            num_col = m["numerator"]
            den_col = m["denominator"]
            num = filtered[num_col].sum()
            den = filtered[den_col].sum() or 1
            value = float(num) / float(den)
        else:
            col = m.get("column")
            if col not in filtered.columns:
                value = float("nan")
            else:
                series = filtered[col]
                if agg == "sum":
                    value = float(series.sum())
                elif agg == "mean":
                    value = float(series.mean())
                elif agg == "count":
                    value = float(series.count())
                elif agg == "nunique":
                    value = float(series.nunique())
                else:
                    value = float("nan")

        results.append(
            {
                "id": m["id"],
                "label": m.get("label", m["id"]),
                "value": value,
                "formatted": _format_value(value, fmt),
            }
        )

    return results


def compute_chart_data(df: pd.DataFrame, chart_cfg: Dict[str, Any], filters: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Compute chart data for a single chart definition.

    Supports simple bar and line charts with aggregation over x.
    """
    filtered = apply_filters(df, config, filters)

    x_col = chart_cfg["x"]
    y_col = chart_cfg["y"]
    agg = chart_cfg.get("aggregation", "sum")

    if x_col not in filtered.columns or y_col not in filtered.columns:
        return {"id": chart_cfg["id"], "label": chart_cfg.get("label", chart_cfg["id"]), "type": chart_cfg.get("type", "bar"), "points": []}

    grouped = filtered.groupby(x_col)[y_col]

    if agg == "sum":
        series = grouped.sum()
    elif agg == "mean":
        series = grouped.mean()
    else:
        series = grouped.sum()

    # Ensure index is sorted for nicer charts
    try:
        series = series.sort_index()
    except TypeError:
        # Mixed types, leave unsorted
        pass

    points = []
    for idx, val in series.items():
        if hasattr(idx, "isoformat"):
            x_val = idx.isoformat()
        else:
            x_val = str(idx)
        points.append({"x": x_val, "y": float(val)})

    return {
        "id": chart_cfg["id"],
        "label": chart_cfg.get("label", chart_cfg["id"]),
        "type": chart_cfg.get("type", "bar"),
        "points": points,
    }
