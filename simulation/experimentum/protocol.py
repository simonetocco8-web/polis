from pathlib import Path
from hashlib import sha256

from archon.contracts import canonical, digest, parse, require

VERSION = "experimentum-1.0"
BASE = "ef1b6dae67c67cf4bf5161eeb8f8a9b5449b9793"
REGIMES = {
    "A": {"status": "institutional-fixture", "missing": ["competizione", "programmi", "elezioni", "mandati e alternanza", "deliberazione e controlli operativi"]},
    "B": {"status": "technical-path", "missing": ["validazione economica", "prove replicate del decisore"]},
    "C": {"status": "institutional-fixture", "missing": ["ordinamento e decisore esteso completi"]},
    "D": {"status": "institutional-fixture", "missing": ["partecipazione umana e deliberazione ibrida operativa"]},
    "E": {"status": "institutional-fixture", "missing": ["elettorato, voto e deliberazione operativi"]},
    "F": {"status": "institutional-fixture", "missing": ["funzione decisionale e obiettivi validati"]},
}
INDICATORS = {
    "gdp": {"unit": "centesimi EUR correnti", "formula": "Somma del valore aggiunto e delle imposte sui prodotti"},
    "units_produced": {"unit": "unità", "formula": "Somma delle unità prodotte"},
    "unemployment_percent": {"unit": "%", "formula": "100 × disoccupati / forza lavoro, nullo se il denominatore è zero"},
    "public_revenue": {"unit": "centesimi EUR correnti", "formula": "Gettito sul reddito e sui consumi nel mese"},
    "public_arrears": {"unit": "booleano", "formula": "Insufficienza nel servizio del debito pubblico"},
    "firm_failures": {"unit": "imprese", "formula": "Imprese cessate nel mese dopo la soglia di arretrati"},
}
TRANSITIONS = {
    "NOT_READY": {"PREREGISTERED"},
    "PREREGISTERED": {"TECHNICAL_VALIDATION", "EXPLORATORY", "CONFIRMATORY_ELIGIBLE", "INVALIDATED"},
    "TECHNICAL_VALIDATION": {"COMPLETED", "INVALIDATED"},
    "EXPLORATORY": {"COMPLETED", "INVALIDATED"},
    "CONFIRMATORY_ELIGIBLE": {"COMPLETED", "INVALIDATED"},
    "COMPLETED": {"REPRODUCED", "INVALIDATED"},
    "REPRODUCED": {"INVALIDATED"},
    "INVALIDATED": set(),
}



def sources():
    root = Path(__file__).resolve().parents[1]
    paths = ("requirements.lock", "config/model-1.json", "config/oikonomia-1.json", "config/stabilitas-1.json",
             "sources/reference-2022.json", "oikonomia/engine.py", "stabilitas/policy.py", "demos/engine.py")
    return {name: sha256((root / name).read_bytes()).hexdigest() for name in paths}

def transition(previous, current):
    require(current in TRANSITIONS.get(previous, ()), "Transizione scientifica non permessa")
    return current


def readiness(scenarios):
    require(type(scenarios) is list and bool(scenarios) and all(x in REGIMES for x in scenarios)
            and len(set(scenarios)) == len(scenarios), "Scenari sconosciuti o duplicati")
    return {"state": "NOT_READY", "scenario_gaps": {s: REGIMES[s]["missing"] for s in scenarios},
            "shared_gaps": ["calibrazione fuori campione", "comparabilità istituzionale verificata",
                            "potenza e regole di confronto validate"]}


def validate(p):
    fields = {"id", "version", "stage", "mode", "objective", "hypothesis", "scenarios", "comparability", "components",
              "initial", "months", "replicas", "shock", "primary", "secondary", "success", "failure", "exclusions",
              "stopping", "statistics", "calibration", "publication", "resources", "budget_api_micro_usd"}
    require(type(p) is dict and p.keys() == fields and p["version"] == VERSION, "Contratto sperimentale sconosciuto")
    for k in ("id", "objective", "hypothesis", "comparability"):
        require(isinstance(p[k], str) and p[k].strip(), "Campo obbligatorio")
    readiness(p["scenarios"])
    require(p["mode"] == "technical" and p["scenarios"] == ["B"], "Il confronto scientifico è bloccato")
    require(p["components"] == dict.fromkeys(("methodos", "demos", "oikonomia", "stabilitas", "nomos", "archon", "theoria"), BASE),
            "Base dei componenti non verificata")
    require(p["initial"] == {"profile": "smoke", "reference": "eu27", "policy": "no-government", "stabilitas": "R"},
            "Configurazione iniziale fuori catalogo")
    stages = {"smoke": (3, 2), "pilot": (12, 6)}
    require(p["stage"] in stages, "L'estensione richiede una nuova validazione")
    months, replicas = stages[p["stage"]]
    require(type(p["months"]) is int and 2 <= p["months"] <= months and type(p["replicas"]) is list
            and 1 <= len(p["replicas"]) <= replicas and
            all(type(s) is int and 0 <= s < 2**64 for s in p["replicas"]) and len(set(p["replicas"])) == len(p["replicas"]),
            "Orizzonte o semi non ammessi")
    require(type(p["budget_api_micro_usd"]) is int and p["budget_api_micro_usd"] == 0, "Budget API non ammesso")
    require(p["shock"] == "production-window-sha256-v1" and p["primary"] == ["gdp"] and
            p["secondary"] == list(INDICATORS)[1:], "Misure o shock fuori catalogo")
    require(p["success"] == ["checkpoint-match", "replay-match", "complete-ledger"]
            and p["failure"] == ["engine-error", "replay-mismatch", "missing-aggregate"]
            and p["exclusions"] == [] and p["stopping"] == "stop-failed-replica-and-record"
            and p["statistics"] == "descriptive-no-causal-inference" and p["calibration"] == "hypothesized"
            and p["publication"] == "aggregate-offline-only" and
            p["resources"] == {"passes_per_replica": 2, "parallelism": 1}, "Regole operative incoerenti")
    return p


def freeze(draft: Path, frozen: Path):
    p = validate(parse(draft.read_bytes()))
    envelope = {"protocol": p, "protocol_sha256": digest(p)}
    with frozen.open("xb") as target:
        target.write(canonical(envelope))
    return envelope


def load(frozen: Path, expected):
    env = parse(frozen.read_bytes())
    require(set(env) == {"protocol", "protocol_sha256"}
            and digest(env["protocol"]) == env["protocol_sha256"] == expected, "Protocollo alterato o anchor inattesa")
    return validate(env["protocol"])
