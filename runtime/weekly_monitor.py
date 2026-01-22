"""
Weekly Runtime Monitor (Stage 5)

- Loads TorchScript model
- Runs weekly inference
- Applies rolling baseline
- Notifies only on sustained 🔴
"""

import torch
import pandas as pd
import numpy as np
from pathlib import Path

from runtime.evaluator import evaluate_weekly
from state.state_manager import load_state, save_state
from data_preprocessing.load_and_clean import load_and_clean
from data_preprocessing.extract_window import extract_lstm_windows


DATA_DIR = Path("data/local")
MODEL_DIR = Path("models")
LOG_PATH = Path("runtime/weekly_log.csv")

WEEKS_PER_MONTH = 4


def _load_model():
    if (MODEL_DIR / "personalized_model.ts").exists():
        return torch.jit.load(MODEL_DIR / "personalized_model.ts")
    return torch.jit.load(MODEL_DIR / "base_model.ts")


def _load_last_n_weeks(n=1):
    csvs = sorted(DATA_DIR.glob("*.csv"))
    return csvs[-7 * n :]


def run_weekly_monitor():
    state = load_state()
    if state["state"] != "runtime":
        return

    model = _load_model()
    model.eval()

    # ---- Load last week data ----
    week_files = _load_last_n_weeks(1)
    if not week_files:
        return

    df = pd.concat([load_and_clean(str(f)) for f in week_files])
    windows = extract_lstm_windows(df)

    X = torch.tensor(windows, dtype=torch.float32)

    with torch.no_grad():
        recon = model(X)
        errors = torch.mean((recon - X) ** 2, dim=(1, 2)).numpy()

    # ---- Load baseline (previous month) ----
    baseline_files = _load_last_n_weeks(WEEKS_PER_MONTH + 1)[:-7]
    baseline_mean = baseline_std = None

    if baseline_files:
        bdf = pd.concat([load_and_clean(str(f)) for f in baseline_files])
        bwindows = extract_lstm_windows(bdf)
        BX = torch.tensor(bwindows, dtype=torch.float32)

        with torch.no_grad():
            brecon = model(BX)
            berrors = torch.mean((brecon - BX) ** 2, dim=(1, 2)).numpy()

        baseline_mean = float(np.mean(berrors))
        baseline_std = float(np.std(berrors))

    # ---- Previous decision ----
    previous_red = False
    if LOG_PATH.exists():
        prev = pd.read_csv(LOG_PATH)
        if not prev.empty:
            previous_red = prev.iloc[-1]["decision"] == "🔴"

    result = evaluate_weekly(
        errors,
        baseline_mean,
        baseline_std,
        previous_week_red=previous_red,
    )

    # ---- Log ----
    LOG_PATH.parent.mkdir(exist_ok=True)
    row = {
        "week_end": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "weekly_mean": result["weekly_mean"],
        "weekly_p95": result["weekly_p95"],
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "decision": result["decision"],
    }

    pd.DataFrame([row]).to_csv(
        LOG_PATH,
        mode="a",
        header=not LOG_PATH.exists(),
        index=False,
    )

    # ---- Notify only if sustained 🔴 ----
    if result["decision"] == "🔴" and previous_red:
        notify_user()


def notify_user():
    # Placeholder: system notification, log, etc.
    print("🔴 Battery anomaly detected (sustained).")


if __name__ == "__main__":
    run_weekly_monitor()
