import json 
from pathlib import Path
from datetime import datetime
from typing import Dict

STATE_PATH = Path("state/state.json")
DATA_DIR = Path("data/local")

WEEKS_FOR_PERSONALIZATION = 4

def _today() -> str :
    return datetime.now().strftime("%Y-%m-%d")

def load_state() -> dict:
    if not STATE_PATH.exists():
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "state" : "warmup",
            "install_date" : _today(),
            "base_model_version" : "v1.0",
            "personalized" : False,
            "weeks_collected" : 0,
            "last_personalization_date" : None,
        }
        save_state(state)
        return state
    
    with STATE_PATH.open() as f:
        return json.load(f)
    

def save_state(state: Dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w") as f:
        json.dump(state, f, indent=2)


def _count_days_collected() -> int:
    if not DATA_DIR.exists():
        return 0
    return len(list(DATA_DIR.glob("*.csv")))


def update_state_progress(state: Dict) -> Dict:
    days = _count_days_collected()
    state["weeks_collected"] = days // 7
    return state


def should_run_personalization(state: Dict) -> bool:
    return (
        state["state"] == "warmup"
        and state["weeks_collected"] >= WEEKS_FOR_PERSONALIZATION
        and not state["personalized"]
    )


def mark_personalized(state: Dict) -> Dict:
    state["state"] = "runtime"
    state["personalized"] = True
    state["last_personalization_date"] = _today()
    return state


def reset_for_new_base_model(state: Dict, new_version: str) -> Dict:
    state["state"] = "warmup"
    state["base_model_version"] = new_version
    state["personalized"] = False
    state["weeks_collected"] = 0
    state["last_personalization_date"] = None
    return state