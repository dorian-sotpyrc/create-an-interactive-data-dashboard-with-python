from __future__ import annotations

import os
from typing import Any, Dict, List, Iterable
import math

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


def _format_value(value, fmt):
    """Format a numeric metric value according to a simple mini-DSL.

    Supported formats:
      - None           → plain str(value)
      - ",d"           → thousands-separated integer (e.g. 1,234)
      - "$,.2f" etc    → currency with thousands separator
      - "0.0", "0.00"  → fixed decimal places (e.g. 9.2, 9.19)
      - "0.0%"         → percentage (value is a ratio, e.g. 0.133 → "13.3%")
      - "0.0x"         → multiplier (e.g. 9.2x)
    Anything else falls back to str(value).
    """
    # Handle None / NaN safely
    if value is None:
        return "-"

    if isinstance(value, (float, int)) and (
        (isinstance(value, float) and math.isnan(value))
        or (isinstance(value, float) and math.isinf(value))
    ):
        return "-"

    if fmt is None:
        return str(value)

    # Integer with thousands separators
    if fmt == ",d":
        try:
            return f"{int(round(value)):,}"
        except Exception:
            return "-"

    # Currency, e.g. "$,.2f" (we only care about decimals)
    if fmt.startswith("$"):
        # default 2 decimal places
        decimals = 2
        if "." in fmt:
            after_dot = fmt.split(".", 1)[1]
            decimals = sum(ch.isdigit() for ch in after_dot)
        try:
            return f"${float(value):,.{decimals}f}"
        except Exception:
            return f"${value}"

    def _decimals_from_pattern(pattern: str) -> int:
        if "." not in pattern:
            return 0
        after = pattern.split(".", 1)[1]
        return sum(ch.isdigit() for ch in after)

    # Percentage formats like "0.0%" or "0.00%"
    if fmt.endswith("%"):
        core = fmt[:-1]
        decimals = _decimals_from_pattern(core)
        try:
            pct = float(value) * 100.0
            return f"{pct:.{decimals}f}%"
        except Exception:
            return str(value)

    # Multiplier formats like "0.0x" or "0.00x"
    if fmt.endswith("x"):
        core = fmt[:-1]
        decimals = _decimals_from_pattern(core)
        try:
            return f"{float(value):.{decimals}f}x"
        except Exception:
            return str(value)

    # Bare numeric formats like "0.0" / "0.00"
    if all(ch in "0.," or ch == "." for ch in fmt):
        decimals = _decimals_from_pattern(fmt)
        try:
            return f"{float(value):.{decimals}f}"
        except Exception:
            return str(value)

    # Fallback: just return str
    return str(value)



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
