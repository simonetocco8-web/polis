"""Independent read-only audit of the bounded Experimentum export."""
import re

from archon.contracts import digest, require

from experimentum.protocol import INDICATORS, REGIMES, VERSION, readiness, sources, validate
from experimentum.statistics import describe

HASH = re.compile("[a-f0-9]{64}")


def verify(report, expected):
    protocol = validate(report["protocol"])
    require(report["version"] == VERSION and report["mode"] == "offline-technical"
            and digest(protocol) == report["protocol_sha256"] == expected
            and report["sources"] == sources() and report["calibration"] == protocol["calibration"] and report["api_calls"] == 0,
            "Fonte o protocollo non verificati")
    replicas = report["replicas"]
    require([r["id"] for r in replicas] == [f"replica-{i}" for i in range(1, len(protocol["replicas"])+1)],
            "Repliche mancanti o duplicate")
    for replica, seed in zip(replicas, protocol["replicas"], strict=True):
        commitment = digest(["experimentum-production-window-v1", seed, protocol["months"]])
        month = 2 + int(commitment[:16], 16) % (protocol["months"] - 1)
        require(replica["shock"] == {"kind": "production-shock", "start": month, "end": month, "commitment": commitment},
                "Calendario esogeno alterato")
        previous = "0"*64
        for month, row in enumerate(replica["series"], 1):
            signature = row["hash"]
            require(set(row) == set(INDICATORS) | {"month", "ledger_sha256", "previous", "hash"}
                    and row["month"] == month and row["previous"] == previous and HASH.fullmatch(row["ledger_sha256"])
                    and digest({k:v for k,v in row.items() if k != "hash"}) == signature, "Catena mensile alterata")
            previous = signature
        if replica["status"] == "REPRODUCED":
            require(replica["error"] is None and len(replica["series"]) == protocol["months"]
                    and previous == replica["anchor"] == replica["replay_anchor"]
                    and HASH.fullmatch(replica["checkpoint_sha256"])
                    and replica["checkpoint_sha256"] == replica["replay_checkpoint_sha256"]
                    and HASH.fullmatch(replica["final_sha256"])
                    and replica["final_sha256"] == replica["replay_final_sha256"], "Prova di riproduzione incoerente")
        else:
            require(replica["status"] == "INVALIDATED" and replica["error"] in protocol["failure"],
                    "Fallimento tecnico non classificato")
    terminal = "REPRODUCED" if all(x["status"] == "REPRODUCED" for x in replicas) else "INVALIDATED"
    require(report["state"] == terminal and report["state_history"] ==
            ["NOT_READY", "PREREGISTERED", "TECHNICAL_VALIDATION", "COMPLETED", terminal]
            and report["readiness"] == readiness(list(REGIMES)) and report["regimes"] == REGIMES
            and report["indicators"] == INDICATORS
            and not report["exclusions"] and report["aggregates"] == describe(replicas, protocol["months"]),
            "Export non riconciliato")
    return {"integrity": "VERIFIED", "technical": terminal, "comparability": "NOT_READY"}
