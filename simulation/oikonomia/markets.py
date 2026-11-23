import numpy as np

from .ledger import apportion


def clear(journal, label, inventory, desired, payer, firms, price, account, stock_limit=None):
    supply = inventory if stock_limit is None else stock_limit
    demand = np.minimum(desired, payer // price)
    units = min(int(supply.sum()), int(demand.sum()))
    purchases = apportion(units, demand)
    sales = apportion(units, supply)
    journal.transfer(label, payer, firms, purchases * price, sales * price, account, "firms")
    inventory -= sales
    return purchases, sales, int(desired.sum()), units


def reprice(price, supply, desired, config):
    imbalance = desired - supply
    step = min(config["price_response_bp"], max(-config["price_response_bp"],
               config["price_response_bp"] * imbalance // max(1, desired, supply)))
    return min(config["price_max"], max(config["price_min"], (price * (10000 + step) + 5000) // 10000))
