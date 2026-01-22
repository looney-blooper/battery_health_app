"""
Weekly Evaluator (Stage 5)

Implements rolling monthly baseline and 🟢🟡🔴 logic.
"""

import numpy as np


def evaluate_weekly(
    weekly_errors,
    baseline_mean,
    baseline_std,
    green_sigma=1.0,
    red_sigma=3.0,
    previous_week_red=False,
):
    weekly_mean = float(np.mean(weekly_errors))
    weekly_p95 = float(np.percentile(weekly_errors, 95))

    decision = "🟢"
    is_red = False

    if baseline_mean is not None and baseline_std is not None:
        if weekly_mean > baseline_mean + red_sigma * baseline_std:
            is_red = True
            decision = "🔴" if previous_week_red else "🟡"
        elif weekly_mean > baseline_mean + green_sigma * baseline_std:
            decision = "🟡"

    return {
        "weekly_mean": weekly_mean,
        "weekly_p95": weekly_p95,
        "decision": decision,
        "is_red": is_red,
    }
