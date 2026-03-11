import streamlit as st
import pandas as pd
import plotly.express as px

from nyc_real_estate_model.utils.rent_loader import get_latest_nyc_rent
from nyc_real_estate_model.utils.vacancy_loader import get_latest_vacancy
from nyc_real_estate_model.utils.inventory_loader import get_latest_inventory
from nyc_real_estate_model.utils.discount_loader import get_latest_discount

from nyc_real_estate_model.analysis.rent_growth import get_rent_growth
from nyc_real_estate_model.analysis.development_timeline import DevelopmentTimeline
from nyc_real_estate_model.analysis.cashflow_model import CashFlowModel
from nyc_real_estate_model.analysis.supply_model import SupplyModel
from nyc_real_estate_model.analysis.market_score import MarketScore

from nyc_real_estate_model.model.income_model import IncomeModel
from nyc_real_estate_model.model.expense_model import ExpenseModel
from nyc_real_estate_model.model.valuation_model import ValuationModel
from nyc_real_estate_model.model.development_cost import DevelopmentCostModel
from nyc_real_estate_model.model.investment_metrics import InvestmentMetrics
from nyc_real_estate_model.model.investment_decision import InvestmentDecision


st.markdown("""
<style>

.section-box {
    border:1px solid #2b2b2b;
    padding:25px;
    border-radius:10px;
    margin-bottom:30px;
    background-color:#0e1117;
}

.analysis-text{
    font-size:24px;
    line-height:1.7;
    font-family:Arial, Helvetica, sans-serif;
}

</style>
""", unsafe_allow_html=True)


st.title("NYC Gateway Development Feasibility Model")

st.header("Project Inputs")

units = st.number_input("Number of Units", 10, 1000, 100)

construction_years = st.number_input("Construction Years", 1, 5, 2)

lease_up_years = st.number_input("Lease-Up Years", 1, 3, 1)

hold_years = st.number_input("Hold Years", 1, 10, 5)

cap_rate = st.slider("Exit Cap Rate", 0.03, 0.08, 0.05)

land_cost = st.number_input("Land Cost ($)", 1_000_000, 50_000_000, 15_000_000)

construction_cost_per_unit = st.number_input(
    "Construction Cost per Unit ($)", 100_000, 800_000, 350_000
)


if st.button("Run Model"):

    avg_monthly_rent = get_latest_nyc_rent(
        "nyc_real_estate_model/data/medianAskingRent_All.csv"
    )

    vacancy_rate = get_latest_vacancy(
        "nyc_real_estate_model/data/NYHVAC.csv"
    )

    inventory = get_latest_inventory(
        "nyc_real_estate_model/data/rentalInventory_All.csv"
    )

    discount_rate = get_latest_discount(
        "nyc_real_estate_model/data/discountShare_All.csv"
    )

    st.header("Market Data")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average NYC Rent", f"${avg_monthly_rent:,.0f}")

    col2.metric("Vacancy Rate", f"{vacancy_rate*100:.1f}%")

    col3.metric("Rental Inventory", f"{inventory:,}")

    col4.metric("Discount Rate", f"{discount_rate*100:.1f}%")


    timeline_model = DevelopmentTimeline()

    timeline_result = timeline_model.build_timeline(
        construction_years,
        lease_up_years,
        hold_years
    )


    income_model = IncomeModel()

    income_result = income_model.calculate(
        units,
        avg_monthly_rent,
        vacancy_rate,
        other_income_per_unit_month=50
    )


    expense_model = ExpenseModel()

    expense_result = expense_model.calculate(
        income_result.effective_gross_income,
        tax_rate=0.012,
        insurance_per_unit=800,
        maintenance_per_unit=1200,
        utilities_per_unit=900,
        management_rate=0.05,
        units=units
    )


    noi = income_result.effective_gross_income - expense_result.total_expenses


    cashflow_model = CashFlowModel()

    cashflow_result = cashflow_model.build_cashflow(
        noi,
        timeline_result.occupancy_curve
    )


    valuation_model = ValuationModel()

    valuation_result = valuation_model.calculate(
        noi,
        cap_rate
    )


    development_model = DevelopmentCostModel()

    development_result = development_model.calculate(
        land_cost,
        construction_cost_per_unit,
        0.25,
        units
    )


    profit = valuation_result.property_value - development_result.total_cost


    st.metric("NOI", f"${noi:,.0f}")

    st.metric("Property Value", f"${valuation_result.property_value:,.0f}")

    st.metric("Development Cost", f"${development_result.total_cost:,.0f}")

    st.metric("Developer Profit", f"${profit:,.0f}")


    growth = get_rent_growth(
        "nyc_real_estate_model/data/medianAskingRent_All.csv"
    )


    rent_projection = []

    for t in range(hold_years):

        rent_t = avg_monthly_rent * (1 + growth) ** (t+1)

        rent_projection.append(rent_t)


    future_rent = rent_projection[-1]

    future_noi = future_rent / avg_monthly_rent * noi


    cap_rate_expansion = 0.005

    exit_cap_rate = cap_rate + cap_rate_expansion

    exit_value = future_noi / exit_cap_rate


    investment_model = InvestmentMetrics()

    investment_result = investment_model.calculate(
        development_result.total_cost,
        cashflow_result.yearly_noi,
        exit_value,
        0.08
    )


    st.header("Investment Metrics")

    st.metric("IRR", f"{investment_result['irr']*100:.2f}%")

    st.metric("NPV", f"${investment_result['npv']:,.0f}")

    st.metric("Equity Multiple", f"{investment_result['equity_multiple']:.2f}x")


    supply_model = SupplyModel()

    supply_model.calculate(
        inventory,
        inventory_growth=0.03
    )


    market_model = MarketScore()

    market_result = market_model.calculate(
        growth,
        vacancy_rate,
        0.03,
        discount_rate
    )


    decision_model = InvestmentDecision()

    decision_result = decision_model.decide(
        investment_result["irr"],
        investment_result["equity_multiple"],
        market_result["market_score"]
    )


    st.header("Investment Decision")

    col1, col2 = st.columns(2)

    col1.metric(
        "Market Score",
        f"{market_result['market_score']*100:.0f}"
    )

    col2.metric(
        "Investment Decision",
        decision_result["decision"]
    )

    st.header("Analysis")

    analysis_html = f"""
    <div class="analysis-text">
    The model indicates an internal rate of return (IRR) of {investment_result['irr'] * 100:.2f}% 
    and an equity multiple of {investment_result['equity_multiple']:.2f}x. Based on the current 
    market data, the average NYC rent is ${avg_monthly_rent:,.0f} with a vacancy rate of 
    {vacancy_rate * 100:.1f}%. The calculated market score is {market_result['market_score']:.2f}, 
    reflecting moderate market conditions.
    <br><br>
    Given the projected development cost of ${development_result.total_cost:,.0f} and an estimated 
    exit value of ${exit_value:,.0f}, the model suggests that the project may generate 
    ${profit:,.0f} in developer profit under the current assumptions.
    <br><br>
    Overall, the model recommends a <strong>{decision_result['decision']}</strong> strategy. This outcome 
    suggests that while the project shows potential under current assumptions, investors should 
    closely monitor rent growth, construction costs, and cap rate changes, as these variables 
    have a significant impact on project returns.
    </div>
    """

    st.markdown(analysis_html, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .analysis-text {
        font-size: 24px;
        line-height: 1.7;
        font-family: Arial, Helvetica, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("IRR Sensitivity Analysis")

    rent_changes = [-0.10, 0, 0.10]
    cap_changes = [-0.01, 0, 0.01]

    irr_matrix = []

    for r in rent_changes:

        row = []

        for c in cap_changes:
            adj_rent = avg_monthly_rent * (1 + r)

            adj_cap = cap_rate + c

            adj_noi = adj_rent / avg_monthly_rent * noi

            adj_exit_value = adj_noi / adj_cap

            adj_investment = investment_model.calculate(
                development_cost=development_result.total_cost,
                yearly_noi=cashflow_result.yearly_noi,
                exit_value=adj_exit_value,
                discount_rate=0.08
            )

            irr_value = adj_investment["irr"] * 100

            row.append(round(irr_value, 2))

        irr_matrix.append(row)

    df_sensitivity = pd.DataFrame(

        irr_matrix,

        index=["Rent -10%", "Base Rent", "Rent +10%"],

        columns=["Cap -1%", "Base Cap", "Cap +1%"]

    )

    fig = px.imshow(

        df_sensitivity,

        text_auto=".2f",

        aspect="auto",

        color_continuous_scale="RdYlGn",

        labels=dict(

            x="Exit Cap Rate Scenario",

            y="Rent Scenario",

            color="IRR (%)"

        )

    )

    fig.update_layout(

        title="IRR Sensitivity Heatmap",

        title_font_size=20

    )

    st.plotly_chart(fig, use_container_width=True)