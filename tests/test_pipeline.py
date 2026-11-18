import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import app as api
from train import fit_reference

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())


def load_data():
    return pd.read_csv(ROOT / "dataset" / "train.csv")


def test_config_is_mine():
    assert CONFIG["student_id"] == "SP23-BAI-048"
    assert len(CONFIG["features"]) == len(CONFIG["weights"])


def test_dataset_is_valid():
    df = load_data()
    assert len(df) >= 100
    assert set(CONFIG["features"] + ["label"]).issubset(df.columns)
    assert df["label"].nunique() == 2


def test_training_gives_useful_model():
    model, accuracy = fit_reference(load_data(), CONFIG)
    assert accuracy >= 0.6
    assert hasattr(model, "predict_proba")


def test_metrics_endpoint():
    client = TestClient(api.app)
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    for key in ["student_id", "accuracy", "training_rows", "model_version", "git_sha"]:
        assert key in body
    assert body["student_id"] == "SP23-BAI-048"
    assert body["training_rows"] >= 100


def test_predict_endpoint():
    client = TestClient(api.app)
    record = {name: 0.5 for name in CONFIG["features"]}
    r = client.post("/predict", json={"records": [record]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["predictions"]) == 1
    assert body["predictions"][0] in (0, 1)
