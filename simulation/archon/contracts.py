import hashlib
import json
import re
from pathlib import Path

VERSION = "archon-1.0"
PROMPT = Path(__file__).with_name("prompt-1.0.txt")
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,63}")
TEXT = ("problem", "objective", "alternative", "rationale", "uncertainty", "expected_effect")
SECRET = re.compile(r"(?:sk-[a-zA-Z0-9_-]{12,}|gh[pousr]_[a-zA-Z0-9_]{15,}|[a-f0-9]{64})")
DECISION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "outcome": {"type": "string", "enum": ["PROPOSE", "ABSTAIN", "INSUFFICIENT_INFORMATION"]},
        "instrument": {"type": ["string", "null"], "enum": ["income-tax", "sales-tax", None]},
        "rate_bp": {"type": ["integer", "null"]}, "duration_months": {"type": ["integer", "null"]},
        **{key: {"type": "string"} for key in TEXT},
    },
}
DECISION_SCHEMA["required"] = list(DECISION_SCHEMA["properties"])


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def parse(raw):
    def object_pairs(pairs):
        values = dict(pairs)
        require(len(values) == len(pairs), "duplicate_fields")
        return values
    def invalid_number(_):
        raise ValueError("invalid_number")

    return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=invalid_number)


def inspect_decision(raw, observation):
    require(isinstance(raw, str) and len(raw.encode()) <= 16000, "invalid_output")
    data = parse(raw)
    require(type(data) is dict and set(data) == set(DECISION_SCHEMA["required"]), "invalid_fields")
    require(data["outcome"] in DECISION_SCHEMA["properties"]["outcome"]["enum"], "invalid_outcome")
    for key in TEXT:
        value = data[key]
        require(isinstance(value, str) and 1 <= len(value.strip()) <= 280 and not SECRET.search(value)
                and not any(ord(char) < 32 or char in "<>" for char in value), "unsafe_rationale")
    if data["outcome"] == "PROPOSE":
        instrument = data["instrument"]
        require(isinstance(instrument, str) and instrument in observation["catalog"], "invalid_instrument")
        rule = observation["catalog"][instrument]
        require(type(data["rate_bp"]) is int and rule["min"] <= data["rate_bp"] <= rule["max"], "invalid_rate")
        require(type(data["duration_months"]) is int and 1 <= data["duration_months"] <= observation["max_duration"]
                and observation["period"] + 1 + data["duration_months"] <= 601, "invalid_duration")
    else:
        require(all(data[key] is None for key in ("instrument", "rate_bp", "duration_months")), "unexpected_policy")
    return data


def proposal(choice, observation, key):
    require(IDENTIFIER.fullmatch(key) and observation["open"], "invalid_period")
    return {
        "version": "1.0", "id": key, "period": observation["period"] + 1, "competence": "fiscal",
        "instrument": choice["instrument"], "targets": ["all-taxpayers"], "parameters": {"rate-bp": choice["rate_bp"]},
        "legal_basis": ["art-28"], "estimated_cost_eur_cents": 0, "funding": "no-spending",
        "duration_months": choice["duration_months"], "expected_effects": choice["expected_effect"],
        "public_rationale": " ".join(choice[key] for key in ("problem", "objective", "rationale"))[:1000],
    }
