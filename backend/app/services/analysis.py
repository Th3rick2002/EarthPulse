"""Trend analysis using Mann-Kendall and calendar-time Sen slope."""

from datetime import date
from itertools import combinations
from statistics import median

import pymannkendall as mk


def compute_trend_analysis(
    values: list[float],
    dates: list[date],
    unit: str,
    frequency: str = "monthly",
) -> dict | None:
    """Compute a Mann-Kendall test and Sen slope in variable units per year."""
    if len(values) < 3:
        return None
    if len(values) != len(dates):
        raise ValueError("values and dates must have the same length")
    if any(current >= following for current, following in zip(dates, dates[1:])):
        raise ValueError("dates must be unique and strictly increasing")

    result = mk.original_test(values)

    # Use elapsed calendar time so missing months do not compress the x-axis.
    slopes_per_year = [
        (later_value - earlier_value)
        / ((later_date - earlier_date).days / 365.2425)
        for (earlier_date, earlier_value), (later_date, later_value)
        in combinations(zip(dates, values), 2)
    ]
    slope_per_year = median(slopes_per_year)
    significant = result.p < 0.05
    direction = "increasing" if slope_per_year > 0 else "decreasing" if slope_per_year < 0 else "stable"
    significance_text = "statistically significant" if significant else "not statistically significant"
    slope_unit = f"{unit}/year"

    interpretation = (
        f"The {frequency} {unit} shows a {direction} trend "
        f"({slope_per_year:.4f} {slope_unit}), which is {significance_text} "
        f"(Mann-Kendall p = {result.p:.4f}). "
        "Note: significance does not imply causation."
    )

    return {
        "method": "mann-kendall",
        "slope": round(slope_per_year, 6),
        "slope_unit": slope_unit,
        "p_value": float(result.p),
        "significant": significant,
        "n_observations": len(values),
        "interpretation": interpretation,
    }


def format_interpretation(slope: float, p_value: float, unit: str, significant: bool) -> str:
    """Format a concise human-readable interpretation."""
    direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    sig_text = "statistically significant" if significant else "not statistically significant"
    return (
        f"The series shows a {direction} trend ({slope:.4f} {unit}/year), "
        f"which is {sig_text} (p = {p_value:.4f}). "
        "Significance does not imply causation."
    )
