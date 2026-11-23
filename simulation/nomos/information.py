from .registry import INSTRUMENTS, month_day, require

# Closed periods only. Units, delays and definitions are part of the protocol.
INDICATORS = {
    "population": ("persone", 0, "Residenti alla chiusura"),
    "employed": ("persone", 1, "Occupati alla chiusura"),
    "unemployment_percent": ("percentuale", 1, "Disoccupati sulla forza lavoro"),
    "gdp": ("centesimi EUR correnti", 1, "PIL nominale mensile riconciliato"),
    "units_produced": ("unità", 0, "Produzione fisica nel mese"),
    "cpi": ("indice", 0, "Prezzo del paniere con riferimento fisso"),
    "median_person_income": ("centesimi EUR correnti", 1, "Reddito mediano modellato"),
    "poverty_percent": ("percentuale", 1, "Povertà relativa modellata"),
    "public_revenue": ("centesimi EUR correnti", 0, "Entrate fiscali nel mese"),
    "public_spending": ("centesimi EUR correnti", 0, "Spesa pubblica nel mese"),
    "public_debt": ("centesimi EUR correnti", 1, "Debito pubblico alla chiusura"),
    "bank_loans": ("centesimi EUR correnti", 1, "Crediti bancari aggregati"),
}


def observation(journal):
    state = journal.state
    require(state.regime == "B", "Canale Archon limitato allo scenario B")
    series = {}
    for key, (unit, delay, definition) in INDICATORS.items():
        observations = [{"period": row["period"], "value": row["indicators"][key]}
                        for row in state.effects if "indicators" in row and row["period"] <= state.period - delay][-6:]
        series[key] = {"unit": unit, "delay": delay, "definition": definition, "calibration": "hypothesized",
                       "available": bool(observations and observations[-1]["value"] is not None), "series": observations}
    receipts = []
    for key, act in state.acts.items():
        if act["author"] != "government":
            continue
        payload = act["payload"]
        receipts.append({"id": key, "state": act["state"], "instrument": payload["instrument"]
                         if payload["instrument"] in INSTRUMENTS else "excluded", "period": payload["period"],
                         "expiry": month_day(payload["period"] + payload["duration_months"]).isoformat(),
                         "applied": act["applied"].isoformat() if act["applied"] else None})
    return {"version": "archon-observation-1", "universe": state.universe, "regime": "B",
            "period": state.period, "day": state.day.isoformat(), "mandate": state.governor,
            "due": state.due.isoformat(),
            "open": state.period < 600 and state.day <= month_day(state.period + 1),
            "nomos": journal.anchor, "indicators": series, "acts": receipts[-12:],
            "catalog": {key: {"min": rule["min"], "max": rule["max"]} for key, rule in INSTRUMENTS.items()},
            "max_duration": state.rules["max_fiscal_duration_months"]}


def receipt(journal, key):
    act = journal.state.acts.get(key)
    if act is None or act["author"] != "government":
        return None
    row = next(event for event in journal.events if event["operation"] == "submit"
               and event["result"]["act"] == key)
    return {"payload": act["payload"], "checks": row["result"]["checks"], "state": act["state"],
            "formal_state": row["result"]["state"], "event": row["hash"]}
