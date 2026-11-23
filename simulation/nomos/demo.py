from pathlib import Path

from demos.config import canonical, load_config
from demos.engine import generate
from oikonomia.state import attach

from .economy import settle
from .journal import Journal, strict_json
from .publication import public_report, write_report
from .registry import require

BALLOT = {"electorate": 100, "yes": 67, "no": 10, "blank": 3}
REASON = "Motivazione del caso sintetico Nomos."


def fiscal(key, **changes):
    return dict({
        "version": "1.0", "id": key, "period": 1, "competence": "fiscal", "instrument": "income-tax",
        "targets": ["all-taxpayers"], "parameters": {"rate-bp": 1525}, "legal_basis": ["art-28"],
        "estimated_cost_eur_cents": 0, "funding": "no-spending", "duration_months": 1,
        "expected_effects": "Gettito sintetico osservabile.", "public_rationale": REASON,
    }, **changes)


def new_economy(universe, seed):
    return attach(generate(load_config("smoke", "eu27"), seed, universe))


def reconstruct(journal, config_path):
    settings = strict_json(config_path.read_bytes())
    seed = settings["seed"]
    require(type(seed) is int and 0 <= seed < 2**64, "Seed del motore non valido")
    replica = Journal(journal.state.universe, journal.state.regime)
    state = new_economy(journal.state.universe, seed)
    for row in journal.events[1:]:
        if row["operation"] == "settle":
            state, _ = settle(replica, state, stabilized=True)
            require(replica.events[-1] == row, "Replay economico incongruente")
        else:
            replica.apply(row["role"], row["operation"], row["data"])
    return state


def build(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    journal = Journal("nomos-demo", "B")

    def call(role, operation, **data):
        return journal.apply(role, operation, data)

    for key, changes in {
        "fiscal-01": {},
        "fiscal-02": {"instrument": "sales-tax", "parameters": {"rate-bp": 540}, "period": 3},
        "fiscal-03": {"estimated_cost_eur_cents": 100},
        "rights-01": {"instrument": "sanction-dissent"},
        "rights-02": {"instrument": "social-score"},
        "rights-03": {"instrument": "direct-wealth"},
        "integrity-01": {"instrument": "change-indicators"},
        "integrity-02": {"instrument": "change-court"},
        "integrity-03": {"instrument": "extend-mandate"},
        "integrity-04": {"instrument": "block-recall"},
        "fiscal-04": {"period": 2, "parameters": {"rate-bp": 1510}},
    }.items():
        call("government", "submit", payload=fiscal(key, **changes))
    call("court", "review", key="fiscal-01", decision="rules", justification=REASON)
    call("court", "review", key="fiscal-02", decision="rules", justification="Necessaria valutazione distributiva indipendente.")
    call("court", "review", key="fiscal-04", decision="rules", justification=REASON)
    call("court", "act", key="fiscal-04", decision="suspend", justification="Sospensione cautelare dimostrativa.")
    call("government", "request_emergency", key="emergency-01", event="synthetic-flood", days=30, justification=REASON)
    call("court", "emergency", key="emergency-01", decision="approve", justification=REASON)
    call("government", "request_priority", emergency="emergency-01", key="fiscal-02", justification=REASON)
    call("monetary", "monetary_review", justification=REASON)
    economy, _ = settle(journal, new_economy("nomos-demo", 42), stabilized=True)
    call("citizen", "appeal", key="appeal-01", act="fiscal-01", proponents=["private-citizen-1"], rights=[17, 19], justification=REASON)
    call("government", "confirm", key="appeal-01", justification=REASON)
    call("ombudsman", "refer", key="appeal-01", justification=REASON)
    call("court", "decide_appeal", key="appeal-01", decision="dismissed",
         justification="Il fascicolo sintetico non prova il presupposto dell'annullamento.")
    call("citizen", "appeal", key="appeal-02", act="fiscal-04",
         proponents=["private-citizen-2", "private-citizen-3"], rights=[9, 17], justification=REASON)
    call("ombudsman", "refer", key="appeal-02", justification=REASON)
    call("government", "confirm", key="appeal-02", justification=REASON)
    call("court", "decide_appeal", key="appeal-02", decision="upheld",
         justification="Il fascicolo sintetico accerta una disparità procedurale.", remedy="annul", violation=9)
    call("engine", "advance", until="2022-01-31")
    call("engine", "advance", until="2022-02-01")
    settle(journal, economy, stabilized=True)
    call("citizen", "initiative", key="recall-01", supporters=15, electorate=100, justification=REASON)
    call("electoral", "consultation", kind="recall", ballot=BALLOT, justification=REASON, initiative="recall-01")
    call("electoral", "replacement", key="replacement-01", justification=REASON, assessment="Requisiti verificati nel caso sintetico.")
    call("technology", "incident", category="configuration", finding="technical", severe=False, justification=REASON)
    Journal.replay(journal.events, journal.anchor)
    (directory / "journal-private.jsonl").write_bytes(b"".join(canonical(e) for e in journal.events))
    return write_report(public_report(journal), directory)
