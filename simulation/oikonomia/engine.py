import numpy as np

from demos.engine import step as demographic_step
from demos.validation import require
from demos.config import canonical, sha

from . import banking, households, labor, national, production, public
from .ledger import Journal
from .markets import clear, reprice
from .state import reconcile

VARIANTS = ("baseline", "recession", "production-shock", "credit-crisis")


def step(state, detail=None, policy=None):
    a, c, d = state.accounts, state.config, state.demographics
    month = d.month + 1
    require(month <= d.config["months"], "End of horizon")
    stress = c["shock_start_month"] <= month <= c["shock_end_month"]
    recession = stress and state.variant == "recession"
    halted = stress and state.variant == "credit-crisis"
    journal = Journal(month, state.journal, detail)
    entries = policy.opening(state, journal) if policy else 0
    price = state.price
    opening_inventory = int(a["inventory"].sum())
    debt_begin = int(a["public_debt"][0])
    spending_start = int(a["government"][0])
    deposit_start = int(a["house_deposit"].sum())
    staff = np.bincount(a["employer"][a["employer"] >= 0], minlength=len(a["active"]))
    banking.lend(state, journal, "firm", np.where(a["active"], staff * c["employee_wage_floor"] * 2 - a["firm_deposit"], 0),
                 c["firm_credit_limit"], halted)
    budget = int(np.count_nonzero(d.people["status"] == 0)) * 38000
    banking.lend(state, journal, "public", np.array([budget - a["government"][0]]), (policy.params.get("treasury_credit_limit_cents", c["public_credit_limit"]) if policy else c["public_credit_limit"]), halted)
    wages = labor.plan(state, recession)
    if policy and month == 1:
        policy.first_month["after_plan"] = a["jobs"].copy()
        policy.first_month["cash_capacity"] = int(a["staff_target"].sum())
    payroll, private_wage_bill = labor.pay_private(state, journal, wages)
    if policy and month == 1:
        policy.first_month["after_payroll"] = a["jobs"].copy()
    producing_workers = int((a["jobs"] == 2).sum())
    physical = {} if policy else None
    output, intermediates = production.produce(state, journal, stress and state.variant == "production-shock", physical)
    produced = int(output.sum())
    # Retain technical inputs for the next production cycle. Closed firms'
    # residual goods become available for liquidation at the same clearing price.
    divisor = policy.params.get("inventory_reserve_divisor", 6) if policy else 6
    reserve = np.where(a["active"], (output + divisor - 1) // divisor + 10, 0)
    def available():
        return np.maximum(a["inventory"] - reserve, 0)

    entitlements = None
    if policy:
        entitlements = public.obligations(state)
    public_pay, transfers = public.pay(state, journal)
    tax = public.tax(state, journal, payroll + public_pay)
    income = payroll + public_pay + transfers - tax
    desired, essential, size = households.demand(state, income, recession)

    sales_tax_unit = price * c["sales_tax_bp"] // 10000
    full_price = price + sales_tax_unit
    potential = np.minimum(desired, a["house_deposit"] // full_price)
    credit_request = np.where((size > 0) & (income > 0), essential * full_price - a["house_deposit"], 0)
    banking.lend(state, journal, "house", credit_request, c["household_credit_limit"], halted)
    potential = np.maximum(potential, np.minimum(desired, a["house_deposit"] // full_price))
    supply = int(available().sum())
    purchases, _, _, consumed = clear(journal, "household-consumption", a["inventory"], potential,
                                    a["house_deposit"], a["firm_deposit"], price, "households", available())
    product_tax = purchases * sales_tax_unit
    sales_tax = int(product_tax.sum())
    journal.transfer("sales-tax", a["house_deposit"], a["government"], product_tax, np.array([sales_tax]), "households", "treasury")
    gov_demand = a["government"] * c["public_goods_bp"] // (10000 * price)
    _, _, public_desired, public_goods = clear(journal, "public-goods", a["inventory"], gov_demand,
                                              a["government"], a["firm_deposit"], price, "treasury", available())
    planned = a["firm_deposit"] * a["active"] * c["private_investment_bp"] // (10000 * price)
    investment, _, firm_desired, firm_investment = clear(journal, "private-investment", a["inventory"], planned,
                                                        a["firm_deposit"], a["firm_deposit"], price, "firms", available())
    planned_public = a["government"] * c["public_investment_bp"] // (10000 * price)
    invested_public, _, invest_desired, public_investment = clear(journal, "public-investment", a["inventory"], planned_public,
                                                                a["government"], a["firm_deposit"], price, "treasury", available())
    depreciation = a["capital"] * c["depreciation_bp"] // 10000
    journal.record("capital-formation", investment * price, investment * price, "firm/capital", "firm/investment-clearing")
    journal.record("public-capital-formation", invested_public * price, invested_public * price, "public/capital", "public/investment-clearing")
    journal.record("fixed-capital-use", depreciation * c["base_price"], depreciation * c["base_price"], "firm/depreciation", "firm/capital")
    a["capital"] += investment - depreciation
    a["public_capital"] += invested_public
    gross_investment = firm_investment + public_investment
    stock_change = int(a["inventory"].sum()) - opening_inventory
    require(stock_change == produced - intermediates - consumed - public_goods - gross_investment, "Goods balance mismatch")

    public_service_due = (int(a["public_debt"][0]) * c["loan_rate_monthly_bp"] // 10000
                          + (int(a["public_debt"][0]) + c["loan_term_months"] - 1) // c["loan_term_months"])
    house_interest, _ = banking.service(state, journal, "house")
    firm_interest, late = banking.service(state, journal, "firm")
    public_interest, public_late = banking.service(state, journal, "public")
    a["arrears"][:] = np.where(late, a["arrears"] + 1, 0)
    failed = (a["arrears"] >= (policy.params.get("arrears_months", 3) if policy else 3)) & (a["active"] == 1)
    credit_losses = banking.write_off(state, journal, failed)
    a["active"][failed] = 0
    private = np.flatnonzero(a["employer"] >= 0)
    fired = private[failed[a["employer"][private]]]
    a["jobs"][fired], a["employer"][fired] = 1, -1

    distributed = policy.distribute(state, journal, house_interest + firm_interest + public_interest) if policy else 0
    interest = public_interest
    public_wages = int(public_pay.sum())
    transfers_total = int(transfers.sum())
    public_revenue = int(tax.sum()) + sales_tax
    public_spending = public_wages + transfers_total + price * (public_goods + public_investment) + interest
    fiscal_balance = public_revenue - public_spending
    public_debt = int(a["public_debt"][0])
    require(int(a["government"][0]) - spending_start == fiscal_balance + public_debt - debt_begin, "Treasury cash mismatch")
    gdp, expenditure, income_gdp, real, surplus = national.accounts(
        price, c["base_price"], produced, intermediates, consumed, public_goods, gross_investment,
        stock_change, public_wages, sales_tax, public_wages + private_wage_bill)
    median, gini, poverty = national.inequality((income // np.maximum(size, 1))[size > 0])
    a["income_history"][:] = income
    regions = labor.regroup(income, d.households["territory"], len(d.territories)).tolist()
    price_next = reprice(price, supply, int(desired.sum()) + public_desired + firm_desired + invest_desired, c)
    if policy and "R" in policy.factors:
        from stabilitas.policy import symmetric_price
        price_next = symmetric_price(price, supply, int(desired.sum()) + public_desired + firm_desired + invest_desired, c)
    state.price = price_next
    reconcile(state)
    event = demographic_step(d)
    labor.advance_demographics(state, event)
    reconcile(state)
    after = a["jobs"]
    unemployed = int((after == 1).sum())
    labor_force = int((after > 0).sum())
    residents = event["final"]
    state.journal = journal.anchor
    stats = {
        "month": month, "population": residents, "firms_active": int(a["active"].sum()),
        "gdp": gdp, "gdp_expenditure": expenditure, "gdp_income": income_gdp, "real_gdp": real,
        "gdp_per_capita": round(gdp / residents) if residents else None,
        "value_added": gdp - sales_tax, "gross_output_value": produced * price, "intermediate_value": intermediates * price,
        "consumption": consumed * full_price, "investment": gross_investment * price, "stock_change": stock_change * price,
        "public_consumption": public_wages + price * public_goods, "wages": public_wages + private_wage_bill, "surplus": surplus,
        "price_cents": price, "next_price_cents": price_next, "cpi": round(100 * full_price / (c["base_price"] + c["base_price"] * c["sales_tax_bp"] // 10000), 6),
        "productivity": round(price * (produced - intermediates) / producing_workers) if producing_workers else None,
        "labor_force": labor_force, "unemployed": unemployed, "employed": labor_force - unemployed,
        "unemployment_percent": round(100 * unemployed / labor_force, 6) if labor_force else None,
        "desired_units": int(desired.sum()), "purchased_units": consumed, "units_produced": produced,
        "inventory_units": int(a["inventory"].sum()), "capital_units": int(a["capital"].sum()),
        "median_person_income": median, "income_gini": gini, "poverty_percent": poverty,
        "household_deposits": int(a["house_deposit"].sum()), "household_deposit_change": int(a["house_deposit"].sum()) - deposit_start,
        "household_debt": int(a["house_debt"].sum()), "firm_deposits": int(a["firm_deposit"].sum()),
        "firm_debt": int(a["firm_debt"].sum()), "public_debt": public_debt, "public_revenue": public_revenue,
        "public_spending": public_spending, "fiscal_balance": fiscal_balance,
        "bank_loans": int(a["bank_loans"][0]), "bank_equity": int(a["bank_equity"][0]),
        "bank_reserves": c["opening_reserves"], "bank_deposits": int(a["house_deposit"].sum() + a["firm_deposit"].sum() + a["government"].sum()),
        "bank_credit_losses": credit_losses, "firm_failures": int(failed.sum()), "public_arrears": bool(public_late[0]),
        "bank_credit_halted": bool(halted or a["bank_equity"][0] <= 0), "income_by_region": regions,
        "cash_balance": int(a["government"][0]), "deprived_households": int(((size > 0) & (purchases < essential)).sum()),
    }
    if policy:
        policy.observe(state, journal, stats, physical, entitlements, public_service_due, entries, distributed, budget)
    return stats, {"journal": journal.anchor, "batches": len(journal.entries), "demography_hash": sha(canonical(event))}
