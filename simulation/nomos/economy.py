from oikonomia.engine import step
from stabilitas.policy import Policy

from .registry import INSTRUMENTS, require


def settle(journal, economy, stabilized=False):
    """Engine-only bridge. Takes effect from the journal, with no proposal argument."""
    state = journal.state
    require(economy.demographics.replica == state.universe and economy.demographics.month == state.period,
            "Universo o checkpoint economico incongruente")
    active = state.policies()
    candidate = economy.clone(state.universe)
    baseline = candidate.config.copy()
    for item in active.values():
        payload = item["payload"]
        candidate.config[INSTRUMENTS[payload["instrument"]]["field"]] = payload["parameters"]["rate-bp"]
    policy = Policy(state.rules["stabilitas_factors"]) if stabilized else None
    stats, _ = step(candidate, policy=policy)
    # Freeze the reference basket for cross-period comparability.
    price = stats["price_cents"]
    full_price = price + price * candidate.config["sales_tax_bp"] // 10000
    base = baseline["base_price"]
    stats["cpi"] = round(100 * full_price / (base + base * baseline["sales_tax_bp"] // 10000), 6)
    candidate.config = baseline
    effect = {key: stats[key] for key in ("public_revenue", "public_spending")}
    journal.apply("engine", "settle", {"period": stats["month"], "receipts": sorted(active), "effect": effect,
                                       "economic_anchor": candidate.journal})
    return candidate, stats
