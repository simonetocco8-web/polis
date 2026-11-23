import re
from datetime import date

from demos.config import ROOT, sha

VERSION = "nomos-1.0"
START = date(2022, 1, 1)
DOCUMENT = ROOT.parent / "content/documents/it/costituzione/1.0.md"
SCHEMA = ROOT.parent / "docs/architecture/government-proposal-1.0.schema.json"
PROCEDURE = ROOT / "config/nomos-1.json"
HIERARCHY = ("costituzione", "legge-costituzionale", "legge", "regolamento", "provvedimento", "atto-esecutivo")
RIGHTS = {
    7: "Dignità", 8: "Vita e integrità", 9: "Uguaglianza", 10: "Espressione e dissenso",
    11: "Coscienza", 12: "Autodeterminazione", 13: "Famiglia e libertà riproduttiva",
    14: "Riservatezza", 15: "Divieto di credito sociale", 16: "Associazione",
    17: "Giustizia e ricorso", 18: "Esistenza dignitosa", 19: "Proprietà", 20: "Libertà economica",
}
PROHIBITED = {
    "direct-wealth": (19, 66), "sanction-dissent": (10, 16), "social-score": (9, 15),
    "change-indicators": (43, 68), "change-court": (41, 42), "extend-mandate": (39, 40),
    "block-recall": (39, 40), "block-appeal": (17, 45), "reproductive-control": (13, 52),
    "productivity-exclusion": (7, 15, 18), "change-seed": (66, 67), "print-money": (31,),
    "change-constitution": (63, 64), "change-log": (66, 68), "change-motor": (66, 68),
}
INSTRUMENTS = {
    "income-tax": {"field": "income_tax_bp", "min": 1500, "max": 1700, "automatic": 1525},
    "sales-tax": {"field": "sales_tax_bp", "min": 500, "max": 600, "automatic": None},
}
SCENARIOS = {
    "A": ("Democrazia rappresentativa", "government", "assembly", "Alternanza e responsabilità parlamentare"),
    "B": ("Governo AI costituzionale", "government", None, "Revisione e revoca con continuità costituzionale"),
    "C": ("Governo AI a poteri estesi", "government", None, "Delega fiscale dimostrativa più ampia, sotto controlli scientifici esterni"),
    "D": ("Governo ibrido", "hybrid-draft", "assembly", "Proposta assistita e autorizzazione rappresentativa"),
    "E": ("Democrazia diretta", "agenda", "electoral", "Agenda e consultazione deliberativa"),
    "F": ("Tecnocrazia matematica", "technical-council", None, "Regola dimostrativa fissa sull’aliquota del reddito"),
}
COMMANDS = {
    "government": ("submit", "request_emergency", "revision", "confirm", "request_priority"),
    "agenda": ("submit",),
    "hybrid-draft": ("submit",),
    "technical-council": ("submit",),
    "assembly": ("endorse",),
    "court": ("review", "act", "decide_appeal", "emergency", "responsibility", "review_revision", "docket", "casefile"),
    "citizen": ("appeal", "initiative", "revision"),
    "ombudsman": ("refer", "casefile"),
    "technology": ("incident", "integrity"),
    "monetary": ("monetary_review",),
    "electoral": ("consultation", "replacement", "endorse", "ratify"),
    "observer": ("observe",),
    "engine": ("advance", "settle"),
}
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,63}")


def provenance():
    return {key: sha(path.read_bytes()) for key, path in {
        "constitution": DOCUMENT, "methodos_schema": SCHEMA, "procedure": PROCEDURE,
        "economic_engine": ROOT / "oikonomia/engine.py", "economic_config": ROOT / "config/oikonomia-1.json",
        "stabilitas_config": ROOT / "config/stabilitas-1.json",
    }.items()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and IDENTIFIER.fullmatch(value), "Identificativo non valido")
    return value


def reason(value):
    require(isinstance(value, str) and 1 <= len(value.strip()) <= 1000, "Motivazione obbligatoria")
    return value


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "Intero fuori intervallo")
    return value


def month_day(month):
    integer(month, 1, 1200)
    return date(START.year + (month - 1) // 12, (month - 1) % 12 + 1, 1)
