import torch
from pathlib import Path

from state.state_manager import (
    load_state,
    save_state,
    should_run_personalization,
    mark_personalized,
)
from data_preprocessing.load_and_clean import load_and_clean
from data_preprocessing.extract_window import extract_lstm_windows
from models.Lstm_2L_AE import LSTM2LayerAutoencoder


BASE_MODEL_PT = Path("trained_models/base_model.pt")
PERSONALIZED_TS = Path("trained_models/personalized_model.ts")
DATA_DIR = Path("data/local")

EPOCHS = 7
LR = 0.0001
BATCH_SIZE = 32

def run_personalization():
    state = load_state()

    if not should_run_personalization(state):
        print("Personalization already completed. Skipping.")
        return
    
    csv_files = sorted(DATA_DIR.glob("*.csv")) [:28]
    if not csv_files:
        print("No data files found for personalization.")
        return
    
    dfs = [load_and_clean(str(f)) for f in csv_files]
    windows = extract_lstm_windows(dfs)

    X = torch.tensor(windows, dtype=torch.float32)

    model = LSTM2LayerAutoencoder(n_features=X.shape[2])
    model.load_state_dict(torch.load(BASE_MODEL_PT))
    model.train()

    for para in model.decoder.parameters():
        para.requires_grad = False

    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)
    loss_fn = torch.nn.MSELoss()
    loader = torch.utils.data.DataLoader(X, batch_size=BATCH_SIZE, shuffle=True)


    for epoch in range(EPOCHS):
        for batch in loader:
            optimizer.zero_grad()
            recon = model(batch)
            loss = loss_fn(recon, batch)
            loss.backward()
            optimizer.step()
        

    model.eval()
    scripted_model = torch.jit.script(model)
    PERSONALIZED_TS.parent.mkdir(parents=True, exist_ok=True)
    scripted_model.save(PERSONALIZED_TS)

    state = mark_personalized(state)
    save_state(state)



if __name__ == "__main__":
    run_personalization()
