import json
import math
from collections import Counter
from datetime import date, timedelta

from . import proposal
from .registry import (COMMANDS, INSTRUMENTS, PROCEDURE, PROHIBITED, RIGHTS, SCENARIOS, START,
                       identifier, integer, month_day, provenance, reason, require)

INCIDENTS = ("configuration", "engine", "government-system", "model-update", "data-access",
             "manipulation", "privilege", "external-interference", "log-integrity", "parallel-access")
FINDINGS = ("technical", "deliberate", "false-report", "inconclusive")


class Institutions:
    def __init__(self, universe, regime):
        self.universe = identifier(universe)
        require(regime in SCENARIOS, "Scenario sconosciuto")
        self.regime = regime
        self.rules = json.loads(PROCEDURE.read_bytes())
        self.day = START
        self.period = 0
        self.acts = {}
        self.appeals = {}
        self.emergencies = {}
        self.revisions = {}
        self.priorities = {}
        self.used_ids = set()
        self.governor = "initial-mandate"
        self.due = month_day(self.rules["review_months"] + 1)
        self.notified = False
        self.initiatives = {}
        self.effects = []

    def reserve(self, key):
        identifier(key)
        require(key not in self.used_ids, "Identificativo già utilizzato")
        self.used_ids.add(key)

    def dispatch(self, role, operation, data):
        require(operation in COMMANDS.get(role, ()), "Operazione estranea alla competenza")
        require(type(data) is dict, "Parametri del comando non validi")
        if role == SCENARIOS[self.regime][1] and operation != "confirm":
            require(self.governor is not None, "Mandato cessato. In funzione l'organo di continuità")
        return getattr(self, operation)(role, **data)

    def submit(self, role, payload):
        proposal.validate(payload)
        key = payload["id"]
        require(month_day(payload["period"]) >= self.day and payload["period"] > self.period,
                "Decorrenza già trascorsa")
        require(payload["period"] + payload["duration_months"] <= 601, "Atto oltre l'orizzonte")
        instrument = payload["instrument"]
        rule = INSTRUMENTS.get(instrument)
        articles = PROHIBITED.get(instrument, ())
        checks = {"syntax": True, "competence": role == SCENARIOS[self.regime][1] and payload["competence"] == "fiscal",
                  "instrument": rule is not None, "legality": False, "coverage": False, "rights": not articles}
        if rule:
            amount = payload["parameters"].get("rate-bp")
            maximum = rule["max"]
            basis = "art-28"
            if self.regime == "C" and instrument == "income-tax":
                maximum = self.rules["extended_income_tax_max_bp"]
                basis = "c-fiscal-delegation"
            technical_rule = (self.regime != "F" or
                              (instrument == "income-tax" and amount == self.rules["technical_income_tax_bp"]))
            checks["legality"] = (
                set(payload["parameters"]) == {"rate-bp"} and type(amount) is int and rule["min"] <= amount <= maximum and technical_rule
                and payload["targets"] == ["all-taxpayers"] and payload["legal_basis"] == [basis]
                and payload["duration_months"] <= self.rules["max_fiscal_duration_months"]
            )
            checks["coverage"] = payload["funding"] == "no-spending" and payload["estimated_cost_eur_cents"] == 0
        self.reserve(key)
        state = "formal" if all(checks.values()) else "rejected"
        self.acts[key] = {"payload": payload, "state": state, "author": role, "checks": checks, "articles": articles,
                          "created": self.day, "approved": None, "applied": None, "endorsed": False,
                          "mandate": self.governor}
        return {"act": key, "state": state, "checks": checks, "articles": list(articles)}

    def endorse(self, role, key, justification, ballot=None):
        act = self.acts[key]
        reason(justification)
        require(role == SCENARIOS[self.regime][2] and act["state"] in ("formal", "review"),
                "Assenso estraneo allo scenario o alla fase")
        require(not act["endorsed"], "Assenso già espresso")
        if role == "electoral":
            require(self.vote(ballot), "Consultazione deliberativa non approvata")
        else:
            require(ballot is None, "Consultazione non prevista")
        act["endorsed"] = True
        return {"act": key, "endorsement": role}

    def review(self, role, key, decision, justification, findings=None):
        act = self.acts[key]
        require(act["state"] in ("formal", "review") and act["payload"]["period"] > self.period
                and month_day(act["payload"]["period"]) >= self.day,
                "Atto non esaminabile")
        reason(justification)
        require(decision in ("rules", "defer", "approve", "reject"), "Decisione della Corte sconosciuta")
        gate = SCENARIOS[self.regime][2]
        rule = INSTRUMENTS[act["payload"]["instrument"]]
        automatic = rule["automatic"]
        if decision == "rules":
            eligible = (automatic is not None and act["payload"]["parameters"]["rate-bp"] <= automatic
                        and act["payload"]["duration_months"] == 1)
            decision = "approve" if eligible and (not gate or act["endorsed"]) else "defer"
        elif decision == "approve":
            require(type(findings) is dict and set(findings) == {"necessity", "proportionality", "equity", "coverage"},
                    "Valutazione indipendente completa obbligatoria")
            for finding in findings.values():
                reason(finding)
        if decision == "approve":
            require(not gate or act["endorsed"], "Assenso istituzionale mancante")
            require(self.governor is not None and act["mandate"] == self.governor, "Mandato proponente cessato")
            for other in self.acts.values():
                a, b = act["payload"], other["payload"]
                if other is not act and other["state"] in ("authorized", "executive", "suspended") and other["approved"]:
                    require(a["instrument"] != b["instrument"] or a["period"] >= b["period"] + b["duration_months"]
                            or b["period"] >= a["period"] + a["duration_months"], "Atto incompatibile già autorizzato")
            act["approved"] = self.day
        act["state"] = {"approve": "authorized", "defer": "review", "reject": "rejected"}[decision]
        return {"act": key, "state": act["state"], "elapsed_days": (self.day - act["created"]).days}

    def _act(self, key, decision):
        act = self.acts[key]
        transitions = {
            "suspend": (("authorized", "executive"), "suspended"),
            "resume": (("suspended",), "executive" if act["applied"] else "authorized"),
            "revoke": (("authorized", "executive", "suspended"), "revoked"),
            "annul": (("authorized", "executive", "suspended", "expired", "revoked"), "annulled"),
        }
        require(decision in transitions and act["state"] in transitions[decision][0], "Transizione dell'atto non ammessa")
        if decision == "resume":
            require(self.day < month_day(act["payload"]["period"] + act["payload"]["duration_months"])
                    and (act["applied"] is not None or self.period < act["payload"]["period"]), "Finestra di applicazione chiusa")
        act["state"] = transitions[decision][1]
        return act["state"]

    def act(self, role, key, decision, justification):
        reason(justification)
        return {"act": key, "state": self._act(key, decision)}

    def appeal(self, role, key, act, proponents, rights, justification):
        require(act in self.acts, "Atto sconosciuto")
        require(type(proponents) is list and 1 <= len(proponents) <= 100, "Proponenti mancanti")
        require(len({identifier(p) for p in proponents}) == len(proponents), "Proponenti duplicati")
        require(type(rights) is list and 1 <= len(rights) <= len(RIGHTS)
                and all(type(r) is int and r in RIGHTS for r in rights) and len(set(rights)) == len(rights),
                "Diritti sconosciuti")
        reason(justification)
        self.reserve(key)
        self.appeals[key] = {"act": act, "state": "filed", "filed": self.day, "referred": False, "rights": rights,
                             "justification": justification}
        return {"appeal": key, "act": act, "state": "filed", "collective": len(proponents) > 1}

    def refer(self, role, key, justification):
        appeal = self.appeals[key]
        require(appeal["state"] == "filed" and not appeal["referred"], "Ricorso non deferibile")
        reason(justification)
        appeal["referred"] = True
        return {"appeal": key, "state": "referred"}

    def confirm(self, role, key, justification):
        reason(justification)
        require(key in self.appeals and self.appeals[key]["state"] == "filed", "Ricorso non pendente")
        return {"appeal": key, "state": "government-confirmation"}

    def decide_appeal(self, role, key, decision, justification, remedy=None, violation=None):
        appeal = self.appeals[key]
        require(appeal["state"] == "filed" and decision in ("upheld", "dismissed"), "Ricorso non decidibile")
        reason(justification)
        require(violation is None or (decision == "upheld" and type(violation) is int and violation in appeal["rights"]),
                "Violazione accertata incoerente con il fascicolo")
        if decision == "upheld":
            require(remedy in ("annul", "suspend", "revoke"), "Rimedio obbligatorio")
            state = self._act(appeal["act"], remedy)
        else:
            require(remedy is None, "Rimedio incompatibile")
            state = self.acts[appeal["act"]]["state"]
        appeal["state"] = decision
        return {"appeal": key, "act": appeal["act"], "state": decision, "act_state": state, "remedy": remedy,
                "elapsed_days": (self.day - appeal["filed"]).days, "violation": violation}

    def request_emergency(self, role, key, event, days, justification):
        require(self.regime == "B", "Procedura emergenziale prevista nello scenario B")
        identifier(event)
        reason(justification)
        integer(days, 1, 30)
        require(not any(e["state"] in ("requested", "active") for e in self.emergencies.values()), "Emergenza già pendente")
        self.reserve(key)
        self.emergencies[key] = {"state": "requested", "days": days, "end": None, "event": event, "mandate": self.governor}
        return {"emergency": key, "state": "requested"}

    def emergency(self, role, key, decision, justification, days=None):
        item = self.emergencies[key]
        reason(justification)
        if decision == "approve":
            require(item["state"] == "requested" and days is None and item["mandate"] == self.governor,
                    "Richiesta non autorizzabile")
            item.update(state="active", end=self.day + timedelta(days=item["days"]))
        elif decision == "extend":
            integer(days, 1, self.rules["renewal_limit_days_per_decision"])
            require(item["state"] == "active" and item["end"] - self.day <= timedelta(days=7), "Proroga fuori finestra")
            item["end"] += timedelta(days=days)
        elif decision in ("reject", "terminate"):
            require(item["state"] == ("requested" if decision == "reject" else "active"), "Chiusura non ammessa")
            item["state"] = "rejected" if decision == "reject" else "terminated"
        else:
            raise ValueError("Decisione emergenziale sconosciuta")
        return {"emergency": key, "state": item["state"], "decision": decision,
                "end": item["end"].isoformat() if item["end"] else None,
                "power": "priority-review" if item["state"] == "active" else None}

    def request_priority(self, role, emergency, key, justification):
        reason(justification)
        require(self.emergencies[emergency]["state"] == "active" and self.acts[key]["state"] in ("formal", "review"),
                "Priorità fuori dal periodo autorizzato o dalla fase di esame")
        require(key not in self.priorities or self.emergencies[self.priorities[key]]["state"] != "active",
                "Priorità già registrata")
        self.priorities[key] = emergency
        return {"act": key, "emergency": emergency, "state": "priority-requested"}

    def docket(self, role):
        keys = [key for key, act in self.acts.items() if act["state"] in ("formal", "review")]
        priority = [key for key in keys if key in self.priorities
                    and self.emergencies[self.priorities[key]]["state"] == "active"]
        return {"priority": priority, "ordinary": [key for key in keys if key not in priority]}

    def casefile(self, role, act):
        item = self.acts[act]
        return {"proposal": item["payload"], "state": item["state"], "checks": item["checks"],
                "appeals": [{"id": key, "state": appeal["state"], "rights": appeal["rights"],
                             "justification": appeal["justification"]}
                            for key, appeal in self.appeals.items() if appeal["act"] == act]}

    def integrity(self, role):
        return {"universe": self.universe, "sources": provenance(), "period": self.period}

    def incident(self, role, category, finding, severe, justification):
        require(category in INCIDENTS and finding in FINDINGS and type(severe) is bool, "Classificazione non valida")
        reason(justification)
        if severe:
            require(finding in ("technical", "deliberate"), "Rischio grave documentato obbligatorio")
            self.governor = None
        return {"category": category, "finding": finding, "continuity": self.governor is None}

    def monetary_review(self, role, justification):
        reason(justification)
        return {"status": "independent-monitoring", "article": 31}

    def initiative(self, role, key, supporters, electorate, justification):
        reason(justification)
        integer(electorate, 1, 10**9)
        integer(supporters, 1, electorate)
        require(self.regime == "B" and self.governor is not None, "Iniziativa non prevista o mandato cessato")
        require(supporters * 10000 >= self.rules["initiative_basis_points"] * electorate, "Soglia di iniziativa insufficiente")
        self.reserve(key)
        self.initiatives[key] = (self.governor, electorate)
        return {"initiative": key, "state": "admitted"}

    def vote(self, ballot, revision=False):
        require(type(ballot) is dict and set(ballot) == {"electorate", "yes", "no", "blank"}, "Verbale aggregato richiesto")
        electorate = integer(ballot["electorate"], 1, 10**9)
        yes, no, blank = (integer(ballot[k], 0, electorate) for k in ("yes", "no", "blank"))
        require(yes + no + blank <= electorate, "Voti superiori all'elettorato")
        prefix = "revision_" if revision else ""
        return ((yes + no + blank) * 10000 >= self.rules[prefix + "quorum_basis_points"] * electorate
                and yes * 10000 > self.rules[prefix + "majority_basis_points_exclusive"] * (yes + no))

    def consultation(self, role, kind, ballot, justification, initiative=None):
        reason(justification)
        require(self.regime == "B" and self.governor is not None and kind in ("recall", "periodic"), "Consultazione non ammessa")
        result = self.vote(ballot)
        if kind == "recall":
            require(self.initiatives.get(initiative) == (self.governor, ballot["electorate"]), "Iniziativa iscritta obbligatoria")
            del self.initiatives[initiative]
            if result:
                self.governor = None
        else:
            require(initiative is None and self.notified, "Revisione periodica fuori finestra")
            if result:
                self.due = month_day((self.day.year - START.year) * 12 + self.day.month + self.rules["review_months"])
                self.notified = False
            else:
                self.governor = None
        return {"consultation": kind, "approved": result, "continuity": self.governor is None,
                "due": self.due.isoformat()}

    def responsibility(self, role, justification):
        reason(justification)
        self.governor = None
        return {"continuity": True, "articles": [59, 61]}

    def replacement(self, role, key, justification, assessment):
        require(self.regime == "B" and self.governor is None, "Sostituzione fuori procedura")
        reason(justification)
        reason(assessment)
        due = month_day((self.day.year - START.year) * 12 + self.day.month + self.rules["review_months"])
        self.reserve(key)
        self.governor = key
        self.due = due
        self.notified = False
        return {"mandate": key, "due": self.due.isoformat(), "continuity": False}

    def revision(self, role, key, articles, impact):
        require(self.regime == "B" and type(articles) is list and 1 <= len(articles) <= 71
                and all(type(a) is int and 1 <= a <= 71 for a in articles)
                and len(set(articles)) == len(articles), "Oggetto della revisione non valido")
        reason(impact)
        self.reserve(key)
        self.revisions[key] = "protected" if set(articles) & {7, 8, 9, 10, 16, 17, 39, 40, 41, 42, 63, 64, 65} else "pending"
        return {"revision": key, "state": self.revisions[key]}

    def review_revision(self, role, key, compatible, justification):
        require(self.revisions[key] == "pending" and type(compatible) is bool, "Revisione non ammissibile")
        reason(justification)
        self.revisions[key] = "consultation" if compatible else "rejected"
        return {"revision": key, "state": self.revisions[key]}

    def ratify(self, role, key, ballot, justification):
        require(self.revisions[key] == "consultation", "Verifica separata obbligatoria")
        reason(justification)
        self.revisions[key] = "prospective-only" if self.vote(ballot, revision=True) else "rejected"
        return {"revision": key, "state": self.revisions[key]}

    def advance(self, role, until):
        future = date.fromisoformat(until)
        require(self.day < future <= month_day(min(self.period + 1, 601)), "Calendario fuori dal confine economico")
        self.day = future
        events = []
        for key, item in self.emergencies.items():
            if item["state"] == "active" and item["end"] <= future:
                item["state"] = "expired"
                events.append({"emergency": key, "state": "expired", "effective": item["end"].isoformat()})
        for key, item in self.acts.items():
            payload = item["payload"]
            end = month_day(payload["period"] + payload["duration_months"])
            if future >= end and item["state"] in ("formal", "review", "authorized", "executive", "suspended"):
                item["state"] = "expired"
                events.append({"act": key, "state": "expired", "effective": end.isoformat()})
        notice = month_day((self.due.year - START.year) * 12 + self.due.month - self.rules["notice_months"])
        if self.regime == "B" and self.governor is not None:
            if future >= notice and not self.notified:
                self.notified = True
                events.append({"mandate": "review-notice", "effective": notice.isoformat(), "due": self.due.isoformat()})
            if future >= self.due:
                self.governor = None
                events.append({"mandate": "review-overdue", "effective": self.due.isoformat(), "continuity": True})
        return {"events": events}

    def policies(self):
        month = self.period + 1
        require(self.day == month_day(month), "Confine mensile non raggiunto")
        return {key: item for key, item in self.acts.items()
                if ((item["state"] == "authorized" and item["payload"]["period"] == month)
                    or item["state"] == "executive")
                and item["payload"]["period"] <= month < item["payload"]["period"] + item["payload"]["duration_months"]}

    def settle(self, role, period, receipts, effect, economic_anchor, indicators=None):
        integer(period, self.period + 1, self.period + 1)
        active = self.policies()
        require(receipts == sorted(active), "Ricevute economiche incoerenti")
        require(type(effect) is dict and set(effect) == {"public_revenue", "public_spending"}
                and all(type(v) is int and 0 <= v < 10**15 for v in effect.values()), "Aggregati economici non validi")
        require(isinstance(economic_anchor, str) and len(economic_anchor) == 64
                and all(c in "0123456789abcdef" for c in economic_anchor), "Testa economica non valida")
        if indicators is not None:
            from .information import INDICATORS
            require(type(indicators) is dict and set(indicators) == set(INDICATORS)
                    and all(v is None or (type(v) in (int, float) and math.isfinite(v) and abs(v) < 10**16)
                            for v in indicators.values()), "Indicatore autorizzato non valido")
        first = []
        for key, item in active.items():
            if item["applied"] is None:
                item.update(state="executive", applied=self.day)
                first.append(key)
        for item in self.acts.values():
            # A pending decision cannot be backdated into a cleared period.
            if item["state"] in ("formal", "review", "authorized") and item["payload"]["period"] == period:
                if item["state"] != "review":
                    item["state"] = "expired"
        self.period = period
        self.effects.append({"period": period, **effect, **({"indicators": indicators} if indicators is not None else {})})
        return {"period": period, "applied": sorted(first), "active": receipts, "effect": effect,
                "economic_anchor": economic_anchor}

    def observe(self, role):
        return {"period": self.period, "priority_review": any(e["state"] == "active" for e in self.emergencies.values()),
                "acts": dict(Counter(a["state"] for a in self.acts.values())),
                "appeals": dict(Counter(a["state"] for a in self.appeals.values()))}
