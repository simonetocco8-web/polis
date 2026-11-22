"""Fetch and derive the only empirical inputs used by Demos."""
import itertools
import json
import math
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from .config import canonical, sha

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
SERIES = {
    "demo_pjan": ("?lang=en&geo=EU27_2020&sinceTimePeriod=2022&untilTimePeriod=2023", "Persone residenti al 1 gennaio per età e sesso, conteggi UE-27", "persone"),
    "demo_mlifetable": ("?lang=en&geo=EU27_2020&time=2022", "qx: probabilità di decesso fra due età esatte, per sesso", "probabilità"),
}


def cells(document):
    dims = [document["dimension"][dim]["category"]["index"] for dim in document["id"]]
    labels = [sorted(dim, key=dim.get) for dim in dims]
    for idx, keys in enumerate(itertools.product(*labels)):
        value = document["value"].get(str(idx))
        if value is not None:
            yield dict(zip(document["id"], keys)), value


def age(label):
    if label == "Y_LT1":
        return 0
    if label == "Y_OPEN":
        return 100
    if label == "Y_GE95":
        return 95
    return int(label[1:])


def derive(raw, manifest):
    ages = {year: [[0] * 101 for _ in range(2)] for year in ("2022", "2023")}
    qx = [[None] * 95 for _ in range(2)]
    for keys, value in cells(json.loads(raw["demo_pjan"])):
        if keys["time"] in ages and keys["sex"] in ("F", "M") and keys["age"] not in ("TOTAL", "UNK"):
            ages[keys["time"]][keys["sex"] == "M"][age(keys["age"])] = int(value)
    for keys, value in cells(json.loads(raw["demo_mlifetable"])):
        if keys["indic_de"] == "PROBDEATH" and keys["sex"] in ("F", "M") and not keys["age"].startswith("Y_GE"):
            qx[keys["sex"] == "M"][age(keys["age"])] = value
    if any(not all(row) for year in ages.values() for row in year):
        raise ValueError("Missing population age/sex cells.")
    if any(not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1 for row in qx for p in row):
        raise ValueError("Missing or invalid mortality probabilities.")
    return {"reference": "UE-27 (EU27_2020)", "fit_year": 2022, "holdout_year": 2023,
            "age_sex_counts": ages, "annual_mortality": qx, "sources": manifest}


def acquire(directory: Path, offline: bool):
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes()) if offline else {}
    raw = {}
    for code, (query, definition, unit) in SERIES.items():
        path = directory / f"{code}.json"
        if offline:
            raw[code] = path.read_bytes()
            if sha(raw[code]) != manifest[code]["sha256"]:
                raise ValueError(f"Source checksum mismatch: {code}")
        else:
            try:
                with urlopen(BASE + code + query, timeout=30) as response:
                    raw[code] = response.read()
            except OSError as exception:
                (directory / "failures.json").write_bytes(canonical({
                    "series": code, "url": BASE + code + query, "error": str(exception),
                    "date": datetime.now(ZoneInfo("Europe/Rome")).date().isoformat(),
                }))
                raise
            manifest[code] = {"agency": "Eurostat", "code": code, "url": BASE + code + query,
                              "geo": "EU27_2020", "period": "2022–2023" if code == "demo_pjan" else "2022",
                              "acquired": datetime.now(ZoneInfo("Europe/Rome")).date().isoformat(),
                              "reuse": "https://ec.europa.eu/eurostat/about-us/policies/copyright",
                              "definition": definition, "unit": unit, "sha256": sha(raw[code]),
                              "transformation": "UE-27 aggregata, celle sesso×età 2022 e confronto 2023; esclusi totali e ignoti; 100+ come 100" if code == "demo_pjan"
                              else "qx per sesso ed età, oltre 94 anni si mantiene qx(94); escluso il valore terminale del gruppo aperto",
                              "limitation": "2023 usato solo come confronto fuori campione trasversale" if code == "demo_pjan" else "periodo 2022 statico, senza proiezione di miglioramento della mortalità"}
    result = derive(raw, manifest)
    if not offline:
        for code, content in raw.items():
            (directory / f"{code}.json").write_bytes(content)
        (directory / "failures.json").unlink(missing_ok=True)
    manifest_path.write_bytes(canonical(manifest))
    (directory / "reference-2022.json").write_bytes(canonical(result))
