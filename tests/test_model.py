import joblib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_model_loads():
    model = joblib.load(ROOT / "model.pkl")
    scaler = joblib.load(ROOT / "scaler.pkl")
    assert model is not None
    assert scaler is not None

def test_predict_shape():
    model = joblib.load(ROOT / "model.pkl")
    scaler = joblib.load(ROOT / "scaler.pkl")

    # dummy row in the same feature order the model expects
    X = pd.DataFrame([[25, 8, 7, 0.7]], columns=["PTS", "REB", "AST", "WIN%"])
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)

    assert preds.shape == (1,), "Model should return one prediction"
