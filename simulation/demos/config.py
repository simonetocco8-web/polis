import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {"smoke": (300, 15), "development": (10_000, 500), "standard": (100_000, 5_000)}
TERRITORIES = ("Centro urbano", "Cintura suburbana", "Distretti rurali")
SECTORS = ("Produzione", "Commercio", "Agricoltura", "Industria", "Servizi")


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_config(profile, reference):
    count, firms = PROFILES[profile]
    model = json.loads((ROOT / "config/model-1.json").read_text())
    if reference == "eu27":
        model["empirical"] = json.loads((ROOT / "sources/reference-2022.json").read_text())
    return dict(model, population=count, firms=firms, profile=profile, reference=reference)
