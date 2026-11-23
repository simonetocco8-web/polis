from statistics import mean, stdev

from .protocol import INDICATORS


def describe(replicas, months):
    rows = []
    for month in range(1, months + 1):
        values = {key: [] for key in INDICATORS}
        for replica in replicas:
            for row in replica["series"]:
                if row["month"] == month:
                    for key in values:
                        if row[key] is not None:
                            values[key].append(row[key])
        rows.append({"month": month, "indicators": {
            key: {"n": len(series), "missing": len(replicas) - len(series),
                  "mean": round(mean(series), 6) if series else None,
                  "sd": round(stdev(series), 6) if len(series) > 1 else None,
                  "range": [min(series), max(series)] if series else None}
            for key, series in values.items()}})
    return rows
