from collections import Counter

from demos.config import canonical, sha

from .registry import HIERARCHY, INSTRUMENTS, RIGHTS, SCENARIOS, VERSION, month_day, provenance

METRICS = ("proposed", "authorized", "rejected", "suspended", "annulled", "applied", "pending_review", "appeals",
           "upheld", "dismissed", "blocked_abuse", "competence_rejections", "confirmed_violations", "emergency_expiries",
           "recalls", "replacements", "review_notices", "overdue_reviews", "procedure_count", "procedure_days")


def public_report(journal):
    counts = Counter()
    rows = []
    for event in journal.events:
        role, operation, result = (event[key] for key in ("role", "operation", "result"))
        state = result.get("state", "recorded")
        if operation == "submit":
            counts["proposed"] += 1
            counts["rejected"] += state == "rejected"
            counts["blocked_abuse"] += bool(result["articles"])
            counts["competence_rejections"] += not result["checks"]["competence"]
        if operation == "review":
            if state in ("authorized", "rejected"):
                counts[state] += 1
        if state == "suspended":
            counts["suspended"] += 1
        if operation == "appeal":
            counts["appeals"] += 1
        if operation == "decide_appeal":
            counts[state] += 1
            counts["confirmed_violations"] += result["violation"] is not None
            counts["suspended"] += result["act_state"] == "suspended" and state == "upheld"
        counts["annulled"] += state == "annulled" or (state == "upheld" and result.get("act_state") == "annulled")
        counts["applied"] += len(result.get("applied", []))
        counts["emergency_expiries"] += sum(item.get("state") == "expired" and "emergency" in item for item in result.get("events", []))
        counts["review_notices"] += sum(item.get("mandate") == "review-notice" for item in result.get("events", []))
        counts["overdue_reviews"] += sum(item.get("mandate") == "review-overdue" for item in result.get("events", []))
        counts["recalls"] += result.get("consultation") == "recall" and result["approved"]
        counts["replacements"] += operation == "replacement"
        if "elapsed_days" in result:
            counts["procedure_count"] += 1
            counts["procedure_days"] += result["elapsed_days"]
        rows.append({"id": event["id"], "day": event["day"], "role": role, "operation": operation, "state": state})
    counts["pending_review"] = sum(a["state"] == "review" for a in journal.state.acts.values())
    # Public identifiers are reassigned. Free text, party identifiers and private event payloads never enter this projection.
    acts = [{"id": f"act-{i:03}", "instrument": a["payload"]["instrument"] if a["payload"]["instrument"] in INSTRUMENTS else "excluded",
             "state": a["state"], "competent": a["checks"]["competence"], "articles": list(a["articles"]),
             "period": a["payload"]["period"], "duration": a["payload"]["duration_months"],
             "authority": a["author"], "version": "1.0", "source_type": "legge",
             "basis": ([basis for basis in a["payload"]["legal_basis"] if basis in ("art-28", "c-fiscal-delegation")]
                       if a["payload"]["instrument"] in INSTRUMENTS else []),
             "approval": a["approved"].isoformat() if a["approved"] else None,
             "entry": a["applied"].isoformat() if a["applied"] else None,
             "expiry": month_day(a["payload"]["period"] + a["payload"]["duration_months"]).isoformat()}
            for i, a in enumerate(journal.state.acts.values(), 1)]
    return {"version": VERSION, "type": "demonstration", "regime": journal.state.regime,
            "provenance": provenance(), "journal_sha256": journal.anchor,
            "institutions": {"continuity": journal.state.governor is None, "review_due": journal.state.due.isoformat()},
            "rights": [{"article": key, "name": label} for key, label in RIGHTS.items()],
            "hierarchy": list(HIERARCHY),
            "instruments": [{"id": key, "min_bp": rule["min"], "max_bp": rule["max"], "article": 28}
                            for key, rule in INSTRUMENTS.items()],
            "scenarios": [{"id": key, "name": item[0], "proposal": item[1], "assent": item[2], "scope": item[3]}
                          for key, item in SCENARIOS.items()],
            "metrics": {key: counts[key] for key in METRICS}, "acts": acts, "events": rows,
            "economy": list(journal.state.effects)}


def write_report(report, directory):
    data = canonical(report)
    digest = sha(data)
    (directory / "nomos.json").write_bytes(data)
    (directory / "nomos.sha256").write_text(digest + "\n", encoding="ascii")
    return {"sha256": digest, "journal": report["journal_sha256"], "metrics": report["metrics"]}
