import numpy as np

from demos.validation import require


def accounts(price, base_price, output, intermediate, consumption, government, investment, stock_change, public_wages, sales_tax, wages):
    # Public nonmarket output valued at direct labour cost. Product tax is added once.
    production = price * (output - intermediate) + public_wages + sales_tax
    spending = price * (consumption + government + investment + stock_change) + public_wages + sales_tax
    surplus = price * (output - intermediate) + public_wages - wages
    income = wages + surplus + sales_tax
    require(production == spending == income, "GDP accounts do not reconcile")
    real = base_price * (output - intermediate) + public_wages + (sales_tax * base_price // price)
    return production, spending, income, real, surplus


def inequality(values):
    if not len(values):
        return None, None, None
    values = np.sort(values.astype(np.float64))
    median = float(np.median(values))
    rank = np.arange(1, len(values) + 1)
    total = values.sum()
    gini = float(2 * (rank * values).sum() / (len(values) * total) - (len(values) + 1) / len(values)) if total else None
    poverty = round(float((values < .6 * median).mean()) * 100, 4) if median > 0 else None
    return round(median), round(max(0, gini), 6) if gini is not None else None, poverty
