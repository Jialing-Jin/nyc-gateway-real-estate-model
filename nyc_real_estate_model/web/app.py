import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st

from nyc_real_estate_model.utils.rent_loader import get_latest_nyc_rent
from nyc_real_estate_model.utils.vacancy_loader import get_latest_vacancy
from nyc_real_estate_model.utils.inventory_loader import get_latest_inventory
from nyc_real_estate_model.utils.discount_loader import get_latest_discount
from nyc_real_estate_model.analysis.rent_growth import get_rent_growth

from nyc_real_estate_model.analysis.development_timeline import DevelopmentTimeline
from nyc_real_estate_model.model.income_model import IncomeModel
from nyc_real_estate_model.model.expense_model import ExpenseModel
from nyc_real_estate_model.model.valuation_model import ValuationModel
from nyc_real_estate_model.model.development_cost import DevelopmentCostModel
from nyc_real_estate_model.analysis.cashflow_model import CashFlowModel
from nyc_real_estate_model.model.investment_metrics import InvestmentMetrics
from nyc_real_estate_model.analysis.market_score import MarketScore
from nyc_real_estate_model.model.investment_decision import InvestmentDecision

st.set_page_config(page_title="NYC Real Estate Development Analyzer", layout="wide")

st.title("NYC Real Estate Development Feasibility Tool")

st.write("Input project assumptions to evaluate development feasibility.")

st.sidebar.header("Project Inputs")

units = st.sidebar.number_input("Number of Units", value=100)

rent = st.sidebar.number_input("Monthly Rent ($)", value=3000)

construction_cost = st.sidebar.number_input("Construction Cost per Unit ($)", value=350000)

land_cost = st.sidebar.number_input("Land Cost ($)", value=15000000)

soft_cost_rate = st.sidebar.number_input("Soft Cost Rate", value=0.25)

cap_rate = st.sidebar.number_input("Exit Cap Rate", value=0.05)

construction_years = st.sidebar.number_input("Construction Years", value=2)

lease_up_years = st.sidebar.number_input("Lease Up Years", value=1)

hold_years = st.sidebar.number_input("Hold Years", value=5)

if st.button("Run Analysis"):

    vacancy_rate = get_latest_vacancy("nyc_real_estate_model/data/NYHVAC.csv")

    inventory = get_latest_inventory("nyc_real_estate_model/data/rentalInventory_All.csv")

    discount_rate = get_latest_discount("nyc_real_estate_model/data/discountShare_All.csv")

    rent_growth = get_rent_growth("nyc_real_estate_model/data/medianAskingRent_All.csv")

    timeline_model = DevelopmentTimeline()

    timeline = timeline_model.build_timeline(construction_years, lease_up_years, hold_years)

    income_model = IncomeModel()

    income = income_model.calculate(units, rent, vacancy_rate, 50)

    expense_model = ExpenseModel()

    expenses = expense_model.calculate(
        income.effective_gross_income,
        0.012,
        800,
        1200,
        900,
        0.05,
        units
    )

    noi = income.effective_gross_income - expenses.total_expenses

    valuation_model = ValuationModel()

    valuation = valuation_model.calculate(noi, cap_rate)

    development_model = DevelopmentCostModel()

    development = development_model.calculate(
        land_cost,
        construction_cost,
        soft_cost_rate,
        units
    )

    cashflow_model = CashFlowModel()

    cashflow = cashflow_model.build_cashflow(
        noi,
        timeline.occupancy_curve
    )

    investment_model = InvestmentMetrics()

    investment = investment_model.calculate(
        development.total_cost,
        cashflow.yearly_noi,
        valuation.property_value,
        0.08
    )

    market_model = MarketScore()

    market = market_model.calculate(
        rent_growth,
        vacancy_rate,
        0.03,
        discount_rate
    )

    decision_model = InvestmentDecision()

    decision = decision_model.decide(
        investment["irr"],
        investment["equity_multiple"],
        market["market_score"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("NOI", f"${noi:,.0f}")
    col2.metric("Property Value", f"${valuation.property_value:,.0f}")
    col3.metric("IRR", f"{investment['irr']:.2%}")
    col4.metric("Equity Multiple", f"{investment['equity_multiple']:.2f}")

    st.subheader("Development Cost")

    st.write(f"Total Development Cost: ${development.total_cost:,.0f}")

    st.subheader("Market Conditions")

    st.write(f"Vacancy Rate: {vacancy_rate:.2%}")
    st.write(f"Rent Growth: {rent_growth:.2%}")
    st.write(f"Market Score: {market['market_score']:.2f}")

    st.subheader("Investment Decision")

    st.write(decision["decision"])

    st.subheader("Analysis Report")

    analysis = f"""
    This development project assumes a monthly rent of {rent}, with {units} units.

    The stabilized Net Operating Income (NOI) is estimated at ${noi:,.0f}.

    Based on the assumed cap rate of {cap_rate:.2%}, the projected property value at stabilization is approximately ${valuation.property_value:,.0f}.

    Total development cost is estimated at ${development.total_cost:,.0f}, which results in an equity multiple of {investment['equity_multiple']:.2f} and an IRR of {investment['irr']:.2%}.

    Current market conditions show a vacancy rate of {vacancy_rate:.2%} and rent growth of {rent_growth:.2%}. The model calculates a market score of {market['market_score']:.2f}.

    Based on financial performance and market conditions, the investment decision is: {decision['decision']}.
    """

    st.write(analysis)