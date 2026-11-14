"""Trend analysis using Mann-Kendall test."""

import pymannkendall as mk
from datetime import date
from typing import Optional


def compute_trend_analysis(
    values: list[float],
    dates: list[date],
    unit: str,
    frequency: str = "monthly",
) -> dict | None:
    """
    Compute Mann-Kendall trend test and Sen's slope.

    Returns dict with analysis results or None if computation fails.
    """
    if len(values) < 3:
        return None

    try:
        # Mann-Kendall test
        result = mk.original_test(values)

        # Sen's slope (Theil-Sen estimator)
        sen_result = mk.sens_slope(values)

        # Interpret slope per year
        if frequency == "monthly":
            slope_per_year = sen_result.slope * 12
            slope_unit = f"{unit}/year"
        else:
            slope_per_year = sen_result.slope
            slope_unit = f"{unit}/{frequency}"

        # Significance at p < 0.05
        significant = result.p < 0.05

        # Interpretation
        direction = "increasing" if sen_result.slope > 0 else "decreasing" if sen_result.slope < 0 else "stable"
        significance_text = "statistically significant" if significant else "not statistically significant"

        interpretation = (
            f"The {frequency} {unit} shows a {direction} trend "
            f"({slope_per_year:.4f} {slope_unit}), which is {significance_text} "
            f"(Mann-Kendall p = {result.p:.4f}). "
            f"Note: significance does not imply causation."
        )

        return {
            "method": "mann-kendall",
            "slope": round(sen_result.slope, 6),
            "slope_unit": slope_unit,
            "p_value": round(result.p, 6),
            "significant": significant,
            "n_observations": len(values),
            "interpretation": interpretation,
        }

    except Exception as e:
        # Log error in production
        return None


def format_interpretation(slope: float, p_value: float, unit: str, significant: bool) -> str:
    """Format human-readable interpretation."""
    direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    sig_text = "statistically significant" if significant else "not statistically significant"
    return (
        f"The series shows a {direction} trend ({slope:.4f} {unit}/period), "
        f"which is {sig_text} (p = {p_value:.4f}). "
        f"Significance does not imply causation."
    )