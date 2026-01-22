import csv
from pathlib import Path
from datetime import datetime

from collector.battery_collector import collect_battery_snapshot

DATA_DIR = Path("data/local")
DATA_DIR.mkdir(parents="True", exist_ok=True)

FIELDS = {
    "timestamp",
    "energy_now",
    "energy_full",
    "energy_full_design",
    "power_now",
    "voltage_now",
    "capacity",
    "cycle_count",
    "status",
}

def _today_csv_path() -> Path:
    today_str = datetime.now().strftime("%Y-%m-%d")
    return DATA_DIR / f"battery_{today_str}.csv"

def log_snapshot() -> None:
    snapshot = collect_battery_snapshot()
    csv_path = _today_csv_path()

    file_exists = csv_path.exists()

    with csv_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(snapshot)


if __name__ == "__main__":
    log_snapshot()
    print("Battery snapshot logged.")