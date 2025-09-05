import pandas as pd
from pathlib import Path

DATA_CSV = Path(__file__).parent.parent / "data_2024_25.csv"

def test_no_missing_values():
    df = pd.read_csv(DATA_CSV)
    assert not df.isnull().any().any(), "Dataset contains NaNs"

def test_required_columns():
    df = pd.read_csv(DATA_CSV)
    required = {"Player", "PTS", "REB", "AST", "WIN%"}
    missing = required - set(df.columns)
    assert not missing, f"Missing columns: {missing}"
