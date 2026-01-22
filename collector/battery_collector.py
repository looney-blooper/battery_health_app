import time
from pathlib import Path
from typing import Dict, Optional

POWER_SUPPLY_PATH = Path("/sys/class/power_supply")

def _read_value(path : Path) -> Optional[float]:
    """
    Docstring for _read_value
    
    :param path: 
    :type path: Path
    :return: 
    :rtype: float | None

    Safely read a numeric value from sysfs.
    Returns None if file does not exist or cannot be read.
    """

    try:
        return float(path.read_text().strip())
    except Exception:
        return None
    

def _read_text(path: Path) -> Optional[str]:
    """
    Safely read a text value from sysfs.
    """
    try:
        return path.read_text().strip()
    except Exception:
        return None


def _detect_battery() -> Optional[Path]:
    """
    Detect BAT* directory.
    """
    for item in POWER_SUPPLY_PATH.iterdir():
        if item.name.startswith("BAT"):
            return item
    return None


def collect_battery_snapshot() -> Dict:
    """
    Collect a battery snapshot
    """

    battery = _detect_battery()

    snapshot = {
        "timestamp" : time.time(),
        "energy_now" : None,
        "energy_full" : None,
        "energy_full_design" : None,
        "power_now" : None,
        "voltage_now" : None,
        "capacity" : None,
        "cycle_count" : None,
        "status" : None,
    }

    if battery is None:
        return snapshot
    
    snapshot["energy_now"] = _read_value(battery / "energy_now")
    snapshot["energy_full"] = _read_value(battery / "energy_full")
    snapshot["energy_full_design"] = _read_value(battery / "energy_full_design")
    snapshot["power_now"] = _read_value(battery / "power_now")
    snapshot["voltage_now"] = _read_value(battery / "voltage_now")
    snapshot["capacity"] = _read_value(battery / "capacity")
    snapshot["cycle_count"] = _read_value(battery / "cycle_count")
    snapshot["status"] = _read_text(battery / "status")
    
    return snapshot


if __name__ == "__main__":
    snapshot = collect_battery_snapshot()
    for key, value in snapshot.items():
        print(f"{key:25s}: {value}")