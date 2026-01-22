from storage.local_logger import log_snapshot
from state.state_manager import (
    load_state,
    save_state,
    update_state_progress,
    should_run_personalization,
)
from personalize.personalize_once import run_personalization
from runtime.weekly_monitor import run_weekly_monitor

def main():
    snapshot = log_snapshot()

    state = load_state()
    state = update_state_progress(state)

    if should_run_personalization(state):
        run_personalization()
        state = load_state()

    if state["state"] == "runtime":
        run_weekly_monitor()

    save_state(state)



if __name__ == "__main__":
    main()





