"""Replayable causal contrasts over the Oikonomia technical model."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import resource
from statistics import median
import time

from demos.config import canonical, load_config, sha
from demos.engine import generate
from demos.snapshot import restore as restore_demos
from demos.validation import require
from oikonomia.engine import step
from oikonomia.snapshot import digest
from oikonomia.state import attach
from stabilitas.policy import Policy, configuration

OPENING = "d12de75af361ccf5fb46d1f972894b0068a6ac3f21273b710e128155a93e2313"
FINAL = "f9aa3a372a02828eb612494f59403de2c06911b5a9e25373a980c1f0ecf2f6b2"
FIRST_SEED = 20261122


def timeline(rows, initial_firms):
    limits = configuration()["thresholds"]
    base = rows[0]

    def find(condition, duration=1):
        streak = 0
        for row in rows:
            streak = streak + 1 if condition(row) else 0
            if streak == duration:
                return row["month"] - duration + 1
        return None

    def below(metric, drop):
        return lambda row: row[metric] * 100 < base[metric] * (100 - drop)

    return {
        "contraction_employment": find(below("employed", limits["employment_drop_percent"])),
        "production_crisis": find(below("units_produced", limits["output_drop_percent"])),
        "persistent_demand_contraction": find(below("desired_units", limits["demand_drop_percent"]), limits["persistent_months"]),
        "firm_credit_cap": find(lambda row: row["firms_at_credit_limit"] > 0),
        "household_credit_cap": find(lambda row: row["households_at_credit_limit"] > 0),
        "public_credit_cap": find(lambda row: row["public_debt"] >= row["public_credit_cap"]),
        "credit_arrears": find(lambda row: row["public_service_shortfall"] > 0),
        "public_transfers_shortfall": find(lambda row: row["transfers_paid"] < row["transfers_due"]),
        "first_firm_failure": find(lambda row: row["firm_failures"] > 0),
        "zero_median_income": find(lambda row: row["median_person_income"] == 0),
        "persistent_low_active_firms": find(lambda row: row["firms_active"] * 100 <= initial_firms *
                                           limits["terminal_active_share_percent"], limits["persistent_months"]),
    }


def run(profile, seed, factor, months, snapshot=None, overrides=None, stress="baseline"):
    if snapshot is None:
        demography = generate(load_config(profile, "eu27"), seed)
    else:
        demography, _ = restore_demos(Path(snapshot))
        require(demography.config["profile"] == profile and demography.seed == seed, "Unexpected input snapshot")
    state = attach(demography, stress)
    opening = digest(state)
    policy = Policy(factor, overrides)
    if policy.factors:
        state.config["stabilitas_sha256"] = policy.provenance()
    initial = digest(state)
    start = time.perf_counter()
    for _ in range(months):
        step(state, policy=policy)
    rows = policy.rows
    last = rows[-1]
    return {
        "profile": profile, "seed": seed, "stress": stress, "experiment": factor, "months": months, "parameters": policy.params,
        "experiment_sha256": policy.provenance(), "demos_sha256": state.origin, "opening_sha256": opening,
        "initial_sha256": initial,
        "final_sha256": digest(state), "journal_sha256": state.journal, "timeline": timeline(rows, len(demography.firms)),
        "first_month": policy.first_month,
        "enterprise_entries_by_sector": [sum(item["sector"] == sector for item in policy.entries) for sector in range(5)],
        "benchmark": {"seconds": round(time.perf_counter() - start, 3), "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
        "metrics": {
            "first_year_gdp_cents": sum(row["gdp"] for row in rows[:12]) if len(rows) >= 12 else None,
            "first_year_output_units": sum(row["units_produced"] for row in rows[:12]) if len(rows) >= 12 else None,
            "last_year_gdp_cents": sum(row["gdp"] for row in rows[-12:]) if len(rows) >= 12 else None,
            "total_interest_cents": sum(sum(row["interest"].values()) for row in rows),
            "total_distributed_cents": sum(row["bank_distribution"] for row in rows),
            "last_unemployment_percent": last["unemployment_percent"], "last_active_firms": last["firms_active"],
            "last_bank_equity_cents": last["bank_equity"], "last_public_debt_cents": last["public_debt"],
            "last_cpi": last["cpi"], "last_deprived_households": last["deprived_households"],
            "total_entries": sum(row["entries"] for row in rows), "total_failures": sum(row["firm_failures"] for row in rows),
        },
        "rows": rows,
    }


def worker(task):
    return run(*task)


def dispersion(runs):
    controls = {(r["seed"], r["stress"]): r for r in runs if r["experiment"] == "control"}
    result = {}
    for name in ("R", "A", "B", "C", "D", "E", "F", "B+C+E", "C25"):
        variations = [r for r in runs if r["experiment"] == name]
        if not variations:
            continue
        pairs = [((r["seed"], r["stress"]), r) for r in variations]
        metrics = {}
        for key in ("last_year_gdp_cents", "last_unemployment_percent", "last_active_firms"):
            values = [r["metrics"][key] - controls[pair]["metrics"][key] for pair, r in pairs
                      if r["metrics"][key] is not None and controls[pair]["metrics"][key] is not None]
            metrics[key] = {"n": len(values), "min": min(values), "median": median(values), "max": max(values)} if values else None
        result[name] = metrics
    return result


def working_task(profile, seed, experiment, months, snapshot=None, stress="baseline"):
    return (profile, seed, "C" if experiment == "C25" else experiment, months, snapshot,
            {"interest_distribution_bp": 2500} if experiment == "C25" else None, stress)


def named_worker(item):
    name, task = item
    result = worker(task)
    result["experiment"] = name
    return result


def study(months, workers, standard_snapshot, explorer_horizon=120):
    require(12 <= months <= 600 and 12 <= explorer_horizon <= 600, "Invalid study horizons")
    names = ("control", "R", "A", "B", "C", "D", "E", "F", "B+C+E", "C25")
    broad = [("standard", FIRST_SEED, name, months, standard_snapshot, "baseline")
             for name in ("control", "R", "C", "B+C+E", "D")]
    small = [("smoke", seed, name, explorer_horizon, None, "recession" if seed == 43 else "baseline")
             for seed in (41, 42, 43) for name in names]
    tasks = [(name, working_task(profile, seed, name, steps, snap, stress)) for profile, seed, name, steps, snap, stress in broad + small]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        all_runs = list(pool.map(named_worker, tasks))
    standards, exploratory = all_runs[:len(broad)], all_runs[len(broad):]
    if months == 600:
        require(standards[0]["opening_sha256"] == OPENING and standards[0]["final_sha256"] == FINAL, "Historical baseline diverged")
    standard_sample(standards)
    for r in exploratory:
        del r["rows"]
    return {
        "schema": "stabilitas-aggregate-1", "release": "0.4.1", "model": "stabilitas-1",
        "status": "prove-tecniche-non-calibrate", "generated_at": datetime.now(timezone.utc).isoformat(), "polis_index": None,
        "historical": {"version": "0.4.0", "opening_sha256": OPENING, "final_sha256": FINAL,
                       "events_sha256": "135af7b434a0472b94f92414aaa388a4bdd70f8a54814541d85c18d0057e00a5"},
        "design": configuration(), "standard": standards, "exploratory": exploratory, "paired_deltas": dispersion(exploratory),
    }


def standard_sample(runs):
    for run in runs[1:]:
        last = run["months"]
        run["rows"] = [row for row in run["rows"] if row["month"] in (1, last) or row["month"] % 12 == 0]


def artifacts(summary, output):
    output.mkdir(parents=True, exist_ok=False)
    payload = canonical(summary)
    (output / "stabilitas.json").write_bytes(payload)
    (output / "stabilitas.sha256").write_text(sha(payload) + "\n")
    with (output / "stabilitas.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        keys = ("month", "gdp", "employed", "units_produced", "desired_units", "inventory_units", "capital_units",
                "household_deposits", "firm_deposits", "cash_balance", "bank_equity", "nonbank_net_financial",
                "public_debt", "transfers_due", "transfers_paid", "real_median_income", "cpi", "entries", "firm_failures")
        writer.writerow(["experiment", *keys])
        for run in summary["standard"]:
            writer.writerows([run["experiment"], *(row[key] for key in keys)] for row in run["rows"])
    baseline = summary["standard"][0]
    rows = baseline["rows"]
    lines = []
    for i, (key, title) in enumerate((("employed", "Occupati"), ("units_produced", "Produzione fisica"), ("cash_balance", "Cassa del Tesoro"))):
        values = [row[key] for row in rows]
        low, high = min(values), max(values)
        points = " ".join(f"{20 + j*580/max(1,len(values)-1):.2f},{i*140 + 120 - (v-low)*85/max(1,high-low):.2f}" for j, v in enumerate(values))
        lines.extend([f'<text x="20" y="{i*140+20}">{escape(title)} · min {low} · max {high}</text>',
                      f'<polyline points="{points}" fill="none" stroke="#745526" stroke-width="2"/>'])
    (output / "baseline.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 425" role="img" aria-label="Tre serie tecniche baseline">' + "".join(lines) + '</svg>')


def main():
    parser = argparse.ArgumentParser(prog="python -m oikonomia.diagnostics")
    parser.add_argument("output", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--months", type=int, default=600)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--exploratory-months", type=int, default=120)
    args = parser.parse_args()
    artifacts(study(args.months, args.workers, args.snapshot, args.exploratory_months), args.output)


if __name__ == "__main__":
    main()
