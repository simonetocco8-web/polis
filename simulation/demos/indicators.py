import numpy as np

from .config import SECTORS, TERRITORIES
from .economy import CLASSES

AGE_LIMITS = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]) * 12
AGES = tuple(f"{start // 12}–{end // 12 - 1}" for start, end in zip(AGE_LIMITS[:-1], AGE_LIMITS[1:])) + ("100+",)
EDUCATION = ("In età scolare o senza titolo inizializzato", "Base", "Secondaria", "Terziaria")
JOBS = ("Fuori forza lavoro", "Disoccupati", "Occupati privati", "Autonomi", "Occupati pubblici")
HEALTH = ("Nessuna limitazione o fragilità assegnata", "Fragilità per fascia d’età", "Limitazioni funzionali")


def counts(values, labels):
    return {label: int(n) for label, n in zip(labels, np.bincount(values, minlength=len(labels)))}


def household_summary(state, p, ages):
    idx = p["household"]
    size = np.bincount(idx, minlength=len(state.households))
    adults = np.bincount(idx[ages >= 216], minlength=len(size))
    children = size - adults
    partnered = np.bincount(idx[p["partner"] >= 0], minlength=len(size))
    # Classify co-residence without inferring kinship from age alone.
    youngest_adult = np.full(len(size), 2000)
    oldest = np.zeros(len(size), dtype=int)
    np.minimum.at(youngest_adult, idx[ages >= 216], ages[ages >= 216])
    np.maximum.at(oldest, idx, ages)
    multi = (adults >= 2) & (oldest - youngest_adult >= 30 * 12)
    category = np.select([adults == 0, size == 1, multi, (adults == 1) & (children > 0),
                          (partnered == 2) & (adults == 2) & (children > 0), (partnered == 2) & (size == 2)],
                         [6, 0, 4, 3, 2, 1], default=5)
    return size, counts(category[size > 0], ("Persone sole", "Coppie", "Coppie con minori", "Un adulto con minori",
                  "Convivenze multigenerazionali", "Altre convivenze", "Nuclei assistiti di soli minori"))


def export(state, manifest):
    mask = state.people["status"] == 0
    p, ages = state.people[mask], state.ages[mask]
    age_band = np.searchsorted(AGE_LIMITS[1:], ages, side="right")
    size, households = household_summary(state, p, ages)
    places = state.households["territory"][p["household"]]
    territories = counts(places, TERRITORIES)
    totals = {"population": len(p), "households": int(np.count_nonzero(size)), "firms": len(state.firms),
              "labor_force": int((p["job"] > 0).sum()), "unemployed": int((p["job"] == 1).sum()),
              "mean_age_years": round(float(ages.mean()) / 12, 2) if len(p) else None}
    totals["unemployment_percent"] = round(100 * totals["unemployed"] / totals["labor_force"], 2) if totals["labor_force"] else None
    calibration = "parziale: età/sesso iniziali e mortalità UE-27 2022" if "empirical" in state.config else "dimostrativo ipotetico"
    return {"schema": "demos-aggregate-1", "snapshot_sha256": manifest["snapshot_sha256"],
            "config_sha256": manifest["config_sha256"], "generator": manifest["generator"],
            "generated_at": manifest["generated_at"], "profile": state.config["profile"], "month": state.month,
            "reference": state.config["reference"], "calibration": calibration,
            "sources": list(state.config.get("empirical", {}).get("sources", {}).values()),
            "totals": totals, "macro_targets": state.config["macro_targets"], "polis_index": None,
            "groups": {"age": counts(age_band, AGES), "age_f": counts(age_band[p["sex"] == 0], AGES),
                       "age_m": counts(age_band[p["sex"] == 1], AGES), "households": households,
                       "education": counts(p["education"], EDUCATION), "employment": counts(p["job"], JOBS),
                       "health": counts(p["health"], HEALTH), "sectors": counts(state.firms["sector"], SECTORS),
                       "firm_sizes": counts(state.firms["size"], CLASSES), "territories": territories,
                       "dwelling_capacity": {label: int(value) for label, value in zip(TERRITORIES, state.territories["dwelling_capacity"])}},
            "definitions": {"employment": "Dotazioni sintetiche; fuori forza lavoro include minori e pensionati.",
                            "households": "Convivenze sintetiche classificate per membri residenti.",
                            "health": "Categorie modellate; non diagnosi o stime cliniche.",
                            "macro": "PIL, inflazione, debito e speranza di vita non sono esiti stimati da Demos."}}


def compare(state):
    empirical = state.config.get("empirical")
    if not empirical:
        return {"status": "no empirical comparison for the hypothetical profile"}
    p = state.people[state.people["status"] == 0]
    years = np.minimum((state.month - p["born"]) // 12, 100)
    sample = np.array([np.bincount(years[p["sex"] == sex], minlength=101) for sex in (0, 1)])
    observed = sample / sample.sum()
    report = {}
    for year, counts_by_sex in empirical["age_sex_counts"].items():
        target = np.asarray(counts_by_sex, dtype=float)
        target /= target.sum()
        cells = [{"sex": "F" if sex == 0 else "M", "age": years, "target_share": float(target[sex, years]),
                  "generated_share": float(observed[sex, years]), "residual": float(observed[sex, years] - target[sex, years])}
                 for sex in (0, 1) for years in range(101)]
        report[year] = {"total_variation": float(np.abs(target - observed).sum() * .5), "cells": cells}
    return {"reference": empirical["reference"], "month": state.month, "fit_year": 2022, "holdout_year": 2023,
            "interpretation": "Cross-sectional diagnostic, not validation of future trajectories.", "comparisons": report}
