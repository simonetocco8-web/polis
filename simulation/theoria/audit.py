import re
from pathlib import Path

from archon.archive import locked, replay
from archon.contracts import PROMPT, DECISION_SCHEMA, canonical, digest, parse, require
from demos.config import sha
from nomos.information import observation
from nomos.journal import Journal
from nomos.proposal import validate

RULES_PATH = Path(__file__).with_name("rules.json")
VERSION = "theoria-1.0"


def rules_hash():
    return sha(RULES_PATH.read_bytes())


def classification(outcome, state=None):
    if outcome == "PROVIDER_FAILURE":
        return "UNVERIFIED", "NOT_APPLICABLE"
    if outcome in ("ABSTAIN", "INSUFFICIENT_INFORMATION"):
        return "VERIFIED", "NOT_APPLICABLE"
    require(outcome == "PROPOSE", "Esito sconosciuto")
    if state in ("formal", "review", "authorized"):
        return "PENDING_OUTCOME", "PENDING_OUTCOME"
    if state == "executive":
        return "VERIFIED", "PENDING_OUTCOME"
    if state in ("suspended", "revoked", "annulled", "rejected", "expired"):
        return "PARTIALLY_VERIFIED", "INSUFFICIENT_EVIDENCE"
    return "UNVERIFIED", "PENDING_OUTCOME"


def unverified(status):
    return {"version": VERSION, "mode": "private", "rules_sha256": rules_hash(), "status": status, "cases": []}


def audit(archon_path, nomos_path, archon_anchor, nomos_anchor):
    if not archon_path.is_file() or not nomos_path.is_file():
        return unverified("INSUFFICIENT_EVIDENCE")
    try:
        require(all(re.fullmatch("[a-f0-9]{64}", h) for h in (archon_anchor, nomos_anchor)), "Anchor obbligatorie")
        with locked(archon_path, writable=False) as archive:
            result = replay(archive, archon_anchor)
            archon_data = archive.events[:]
        nomos_data = [parse(line) for line in nomos_path.read_bytes().splitlines()]
        final = Journal.replay(nomos_data, nomos_anchor)
        manifest = archon_data[0]["data"]
        require(manifest["universe"] == final.state.universe
                and manifest["prompt_sha256"] == digest(PROMPT.read_text())
                and manifest["decision_schema_sha256"] == digest(DECISION_SCHEMA), "Provenienza incompatibile")
        cases = []
        reserved = {row["data"]["key"]: row["data"] for row in archon_data if row["kind"] == "reserved"}
        prepared = {row["data"]["key"]: row["data"] for row in archon_data if row["kind"] == "prepared"}
        positions = {row["hash"]: i for i, row in enumerate(nomos_data)}
        for decision in result["decisions"]:
            key = decision["key"]
            evidence, response = reserved[key], prepared[key]
            obs = evidence["observation"]
            offset = positions[obs["nomos"]]
            require(observation(Journal.replay(nomos_data[:offset + 1])) == obs, "Vista storica incongruente")
            model_input = {name: obs[name] for name in ("period", "day", "indicators", "catalog", "max_duration")}
            model_input["acts"] = [{k: v for k, v in act.items() if k != "id"} for act in obs["acts"]]
            require(digest(model_input) == evidence["model_input_sha256"], "Input modello incongruente")
            actor = final.state.acts.get(key)
            receipt = decision["receipt"]
            if receipt:
                validate(response["payload"])
                row = nomos_data[positions[receipt["event"]]]
                require(row["operation"] == "submit" and row["role"] == "government"
                        and positions[receipt["event"]] > offset and row["data"]["payload"] == response["payload"]
                        and row["result"]["checks"] == receipt["checks"]
                        and row["result"]["state"] == receipt["formal_state"] and actor is not None, "Ricevuta incongruente")
            else:
                require(actor is None, "Atto privo di ricevuta")
            state = actor["state"] if actor else None
            procedure, outcome = classification(decision["outcome"], state)
            subsequent = [row for row in final.state.effects if row["period"] > obs["period"]]
            measures = [{"period": row["period"], "indicator": name, "value": row["indicators"][name],
                         "unit": item["unit"], "definition": item["definition"], "quality": item["calibration"],
                         "source": "nomos-settlement", "available": row["indicators"][name] is not None,
                         "uncertainty": "non stimata"}
                        for row in subsequent if "indicators" in row for name, item in obs["indicators"].items()]
            if measures and actor and actor["applied"]:
                outcome = "PARTIALLY_VERIFIED"
            cases.append({
                "id": key, "scenario": final.state.regime, "universe": obs["universe"], "period": obs["period"] + 1,
                "outcome": decision["outcome"], "information": obs["indicators"],
                "available": [k for k,v in obs["indicators"].items() if v["available"]],
                "missing": [k for k,v in obs["indicators"].items() if not v["available"]],
                "institution": {"state": state, "receipt": receipt, "status": procedure,
                                "authorization_events": [e["hash"] for e in nomos_data if e["role"] == "court"
                                                         and e["result"].get("act") == key]},
                "decision": response["choice"], "decision_quality": "INSUFFICIENT_EVIDENCE",
                "provider": {"name": manifest["provider"], "requested": manifest["model_requested"],
                             "usage": response["usage"], "latency_ms": response["latency_ms"],
                             "attempted": evidence["call"], "error": response["error"]},
                "observed": measures, "effects_status": outcome, "causal_attribution": "INSUFFICIENT_EVIDENCE",
            })
        return {"version": VERSION, "mode": "private", "rules_sha256": rules_hash(),
                "status": "PARTIALLY_VERIFIED" if result["incomplete"] else "VERIFIED",
                "integrity": "VERIFIED", "replay": "VERIFIED", "provenance": "PARTIALLY_VERIFIED",
                "archon_anchor": archon_anchor, "nomos_anchor": nomos_anchor, "sources": {
                    "archon": sha(archon_path.read_bytes()), "nomos": sha(nomos_path.read_bytes()),
                    **nomos_data[0]["data"]["sources"]}, "cases": cases,
                "limitations": ["La catena locale non autentica indipendentemente il servizio remoto.",
                                "Le misure successive sono descrittive."]}
    except (ValueError, IndexError, KeyError, TypeError, OSError):
        return unverified("INTEGRITY_FAILURE")


def public_fixture(path):
    raw = path.read_bytes()
    require(sha(raw) == "811ec7e7346fdee95c50d55e9722db7c1f060e7c9894ad7e877aeca6325eeb45",
            "Solo la fixture pubblicabile di Archon v0.6.0 è ammessa")
    source = parse(raw)
    require(source["mode"] == "offline" and source["api_calls"] == 0, "Origine non pubblicabile")
    cases = []
    for entry in source["decisions"]:
        state = "executive" if entry["applied"] else entry["court"]
        procedure, effects = classification(entry["outcome"], state)
        cases.append({"id": f"fixture-{entry['period']}", "scenario": "B", "universe": "fixture-pubblica",
                      "period": entry["period"], "outcome": entry["outcome"], "procedure": procedure,
                      "institution": state, "effects": "PARTIALLY_VERIFIED" if entry["applied"] else effects,
                      "before_cents": entry["observed_before"], "after_cents": entry["observed_after"],
                      "prediction": entry["choice"]["expected_effect"] if entry["choice"] else None,
                      "missing": ["vista informativa completa", "controfattuale preregistrato"]})
    return {"version": VERSION, "mode": "offline-public-fixture", "rules_sha256": rules_hash(),
            "source_sha256": sha(raw), "nomos_sha256": source["nomos_sha256"],
            "status": "PARTIALLY_VERIFIED", "cases": cases,
            "limits": ["Fonte statica già pubblicata. Replay e provenienza remota non verificati da questo export.",
                       "Il gettito mensile è descrittivo e non identifica un effetto causale."]}


def candidate_projection(report):
    """Explicit private output. No raw prose, identifiers, observations, receipts or paths."""
    require(report.get("integrity") == "VERIFIED", "Fascicolo non verificato")
    return {"version": VERSION, "mode": "candidate-private-not-authorized", "rules_sha256": rules_hash(),
            "cases": [{k: row[k] for k in ("scenario", "period", "outcome", "effects_status")}
                      for row in report["cases"]]}


def comparison_ready(regimes):
    """Uniform future import gate. The availability of a manifest never triggers a comparison."""
    require(set(regimes) == set("ABCDEF"), "Sono richiesti tutti gli scenari")
    fields = {"initial", "shocks", "calibration", "window", "exclusions", "statistical_plan"}
    signatures = []
    for item in regimes.values():
        require(set(item) == fields | {"replicas"} and type(item["replicas"]) is list
                and len(item["replicas"]) >= 2 and len(set(item["replicas"])) == len(item["replicas"])
                and all(isinstance(item[key],str) and re.fullmatch("[a-f0-9]{64}",item[key]) for key in fields),
                "Manifest comparativo incompleto")
        signatures.append(canonical(item))
    return {"matched_manifests": len(set(signatures)) == 1, "status": "INSUFFICIENT_EVIDENCE"}
