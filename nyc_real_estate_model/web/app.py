import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NYC RE Feasibility",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""

<style>

/* Force main app into readable light mode */
.stApp {
    background-color: #ffffff !important;
}

/* Main content background */
[data-testid="stAppViewContainer"],
[data-testid="block-container"] {
    background-color: #ffffff !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f5f7fa !important;
}

/* Normal text only, do not target all div/span globally */
h1, h2, h3, h4, h5, h6,
p, label,
[data-testid="stMarkdownContainer"] {
    color: #1f2933 !important;
}

/* Primary button */
div.stButton > button[kind="primary"] {
    background-color: #edf3f9 !important;
    color: #163a5c !important;
    border: 3px solid #2f5d8c !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

/* Hover */
div.stButton > button[kind="primary"]:hover {
    background-color: #2f5d8c !important;
    color: #ffffff !important;
    border: 3px solid #1f4e79 !important;
}

/* Number input text */
input {
    background-color: #ffffff !important;
    color: #1f2933 !important;
}

/* Number input +/- buttons */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background-color: #0c2340 !important;
    color: #ffffff !important;
    border: none !important;
}

/* Hover */
button[data-testid="stNumberInputStepUp"]:hover,
button[data-testid="stNumberInputStepDown"]:hover {
    background-color: #163a5c !important;
}

/* Remove Streamlit top header spacing */
header[data-testid="stHeader"] {
    background: transparent;
    height: 0rem;
}

/* Move toolbar slightly right */
[data-testid="stToolbar"] {
    right: 1rem;
}

/* Reduce top page padding */
/* Reduce top spacing and widen layout */
.block-container {
    padding-top: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ===== Option C — Deep Blue & Steel palette ===== */
:root {
    --c-primary: #0c2340;   /* deep navy */
    --c-accent:  #1f4e79;   /* steel blue */
    --c-muted:   #6b8cae;   /* light steel */
    --c-surface: #f5f7fa;   /* near-white surface */
    --c-line:    #e2e8f0;   /* hairline */
}

/* Headings & titles */
/* Typography hierarchy */
h1 {
    color: var(--c-primary) !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
    line-height: 1.15;
}

h2 {
    color: var(--c-primary) !important;
    font-size: 1.9rem !important;
    font-weight: 650 !important;
    line-height: 1.25;
}

h3 {
    color: var(--c-primary) !important;
    font-size: 1.35rem !important;
    font-weight: 600 !important;
    line-height: 1.3;
}

/* Metric numbers */
/* Metric values */
[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 650 !important;
    color: #1f2933 !important;
    line-height: 1.15;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #5b6b7a !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    text-transform: none !important;
}

/* Tabs */
/* Tabs */
button[data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 550 !important;
    color: #5b6b7a !important;
    padding-left: 0.2rem !important;
    padding-right: 1.2rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--c-primary) !important;
    font-weight: 650 !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #2f5d8c !important;
    height: 2.5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] { background-color: var(--c-surface); }
section[data-testid="stSidebar"] .stNumberInput { margin-bottom: 0.2rem; }

.section-divider {
    border: none;
    border-top: 1px solid var(--c-line);
    margin: 1.2rem 0;
}

/* Unified analysis typography */
.analysis-section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.8;
    color: #2c3e50;
    margin-bottom: 1.5rem;
}
.analysis-section h3 {
    font-size: 17px;
    font-weight: 600;
    color: #0c2340;
    margin-top: 1.5rem;
    margin-bottom: 0.6rem;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.3rem;
    font-family: inherit;
}
.analysis-section p {
    margin: 0.4rem 0;
    font-family: inherit;
}
.analysis-section .highlight {
    font-weight: 600;
    color: #1f4e79;
}
.analysis-section .note {
    font-size: 13px;
    color: #6b8cae;
    font-style: italic;
    background: #f5f7fa;
    padding: 0.6rem 0.9rem;
    border-left: 3px solid #1f4e79;
    margin-top: 1rem;
    border-radius: 0 4px 4px 0;
}

/* Decision badges — deep blue family */
.badge-buy  { display: inline-block; background: #e8eef4; color: #0c2340; font-weight: 600; font-size: 1rem; padding: 0.3rem 1rem; border-radius: 20px; border: 1px solid #1f4e79; }
.badge-hold { display: inline-block; background: #fdf4e3; color: #7a5012; font-weight: 600; font-size: 1rem; padding: 0.3rem 1rem; border-radius: 20px; border: 1px solid #d4a24e; }
.badge-pass { display: inline-block; background: #f7e8e8; color: #7a1f1f; font-weight: 600; font-size: 1rem; padding: 0.3rem 1rem; border-radius: 20px; border: 1px solid #b34a4a; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar inputs ────────────────────────────────────────────────────────────
# Sidebar inputs
st.sidebar.header("Project Inputs")

run = st.sidebar.button("▶  Run Analysis", use_container_width=True, type="primary")

units = st.sidebar.number_input(
    "Number of Units", min_value=1, value=100, step=1
)
rent = st.sidebar.number_input(
    "Monthly Rent ($)", min_value=500, value=3000, step=50
)
construction_cost = st.sidebar.number_input(
    "Construction Cost per Unit ($, excl. land)",
    min_value=100000, value=500000, step=50000,
    help="NYC/NJ rental construction typically $400K-$1M+ per unit (excluding land)."
)
land_cost = st.sidebar.number_input(
    "Land Cost ($)",
    min_value=500000, value=15000000, step=500000,
    help="Land cost is highly location-dependent and calculated separately."
)
cap_rate = st.sidebar.number_input(
    "Exit Cap Rate",
    min_value=0.01, max_value=0.15,
    value=0.05, step=0.0025, format="%.4f",
    help="Step size is 25 basis points (0.25%)."
)

# Advanced settings (collapsed to keep the sidebar short)
with st.sidebar.expander("Advanced settings"):
    soft_cost_rate = st.number_input(
        "Soft Cost Rate",
        min_value=0.0, max_value=0.5,
        value=0.25, step=0.01, format="%.2f"
    )
    construction_years = st.number_input(
        "Construction Years", min_value=1, max_value=10, value=2, step=1
    )
    lease_up_years = st.number_input(
        "Lease-Up Years",
        min_value=0.5, max_value=3.0,
        value=1.0, step=0.5, format="%.1f",
        help="Typical lease-up period is 1 to 2.5 years."
    )
    hold_years = st.number_input(
        "Hold Years", min_value=1, max_value=20, value=5, step=1
    )

# ── Main header ───────────────────────────────────────────────────────────────
st.title("NYC Real Estate Development Feasibility Tool")
st.caption("Input project assumptions in the sidebar, then click **Run Analysis**.")

if not run:
    st.info("Configure inputs in the sidebar and click **Run Analysis** to begin.")
    st.stop()

# ── Load market data ──────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    vacancy_rate  = get_latest_vacancy(os.path.join(BASE_DIR, "nyc_real_estate_model", "data", "NYHVAC.csv"))
    inventory     = get_latest_inventory(os.path.join(BASE_DIR, "nyc_real_estate_model", "data", "rentalInventory_All.csv"))
    discount_rate = get_latest_discount(os.path.join(BASE_DIR, "nyc_real_estate_model", "data", "discountShare_All.csv"))
    rent_growth   = get_rent_growth(os.path.join(BASE_DIR, "nyc_real_estate_model", "data", "medianAskingRent_All.csv"))

# ── Run models ────────────────────────────────────────────────────────────────
timeline_model = DevelopmentTimeline()
# build_timeline needs integer years; round lease_up_years (e.g. 1.5) up to nearest int
import math
timeline = timeline_model.build_timeline(
    int(construction_years),
    int(math.ceil(lease_up_years)),
    int(hold_years)
)

income_model = IncomeModel()
income = income_model.calculate(units, rent, vacancy_rate, 50)

expense_model = ExpenseModel()
expenses = expense_model.calculate(
    income.effective_gross_income,
    0.012, 800, 1200, 900, 0.05, units
)

noi = income.effective_gross_income - expenses.total_expenses

valuation_model = ValuationModel()
valuation = valuation_model.calculate(noi, cap_rate)

development_model = DevelopmentCostModel()
development = development_model.calculate(land_cost, construction_cost, soft_cost_rate, units)

cashflow_model = CashFlowModel()
cashflow = cashflow_model.build_cashflow(noi, timeline.occupancy_curve)

investment_model = InvestmentMetrics()
investment = investment_model.calculate(
    development.total_cost,
    cashflow.yearly_noi,
    valuation.property_value,
    0.08
)

market_model = MarketScore()
market = market_model.calculate(rent_growth, vacancy_rate, 0.03, discount_rate)

decision_model = InvestmentDecision()
decision = decision_model.decide(
    investment["irr"],
    investment["equity_multiple"],
    market["market_score"]
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_sensitivity, tab_cashflow, tab_analysis = st.tabs([
    "Overview",
    "Sensitivity",
    "Cash Flows",
    "Analysis",
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab_overview:

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NOI",             f"${noi:,.0f}")
    c2.metric("Property Value",  f"${valuation.property_value:,.0f}")
    c3.metric("IRR",             f"{investment['irr']:.2%}")
    c4.metric("Equity Multiple", f"{investment['equity_multiple']:.2f}x")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("Development Cost")
        hard_cost = construction_cost * units
        soft_cost = hard_cost * soft_cost_rate
        fig_cost = go.Figure(go.Pie(
            labels=["Land", "Hard Cost", "Soft Cost"],
            values=[land_cost, hard_cost, soft_cost],
            hole=0.45,
            marker_colors=["#0c2340", "#1f4e79", "#6b8cae"],
            textinfo="label+percent",
            hovertemplate="%{label}: $%{value:,.0f}<extra></extra>",
        ))
        fig_cost.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=330,
            annotations=[dict(
                text=f"${development.total_cost/1e6:.1f}M",
                x=0.5, y=0.5, font_size=18, showarrow=False,
                font_color="#0c2340"
            )]
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        st.caption(f"Total Development Cost: **${development.total_cost:,.0f}**")

    with right:
        st.subheader("Market Conditions")
        st.metric("Vacancy Rate",      f"{vacancy_rate:.2%}")
        st.metric("Rent Growth",       f"{rent_growth:.2%}")
        st.metric("Rental Inventory",  f"{inventory:,}")
        st.metric("Discount Share",    f"{discount_rate:.2%}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("Investment Decision")
    dec_text  = decision["decision"].lower()
    badge_cls = (
        "badge-buy"  if "buy"  in dec_text else
        "badge-hold" if "hold" in dec_text else
        "badge-pass"
    )
    score_pct = market["market_score"] * 100

    dcol1, dcol2 = st.columns([1, 2])
    with dcol1:
        st.metric("Market Score", f"{score_pct:.0f} / 100")
    with dcol2:
        st.markdown(
            f'<p style="margin-top:1rem">Decision: '
            f'<span class="{badge_cls}">{decision["decision"]}</span></p>',
            unsafe_allow_html=True,
        )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — SENSITIVITY (cap rate ±50bp / ±100bp per tutor)
# ═════════════════════════════════════════════════════════════════════════════
with tab_sensitivity:

    st.subheader("IRR Sensitivity — Rent × Exit Cap Rate")
    st.caption("Each cell shows IRR (%). Cap rate moves shown at 50 bp increments.")

    rent_scenarios = {
        "Rent −10%": rent * 0.90,
        "Rent −5%":  rent * 0.95,
        "Base Rent":  rent,
        "Rent +5%":  rent * 1.05,
        "Rent +10%": rent * 1.10,
    }
    cap_scenarios = {
        "Cap −100bp": cap_rate - 0.0100,
        "Cap −50bp":  cap_rate - 0.0050,
        "Base Cap":    cap_rate,
        "Cap +50bp":  cap_rate + 0.0050,
        "Cap +100bp": cap_rate + 0.0100,
    }

    irr_matrix = []
    for rent_val in rent_scenarios.values():
        row = []
        for cap_val in cap_scenarios.values():
            adj_income = income_model.calculate(units, rent_val, vacancy_rate, 50)
            adj_noi    = adj_income.effective_gross_income - expenses.total_expenses
            adj_exit   = adj_noi / max(cap_val, 0.001)
            adj_inv    = investment_model.calculate(
                development.total_cost,
                cashflow.yearly_noi,
                adj_exit,
                0.08
            )
            row.append(round(adj_inv["irr"] * 100, 2))
        irr_matrix.append(row)

    df_irr = pd.DataFrame(
        irr_matrix,
        index=list(rent_scenarios.keys()),
        columns=list(cap_scenarios.keys()),
    )

    fig_irr = px.imshow(
        df_irr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        zmin=0,
        zmax=max(18, df_irr.values.max()),
        labels=dict(x="Exit Cap Rate Scenario", y="Rent Scenario", color="IRR (%)"),
    )
    fig_irr.update_layout(
        title="IRR Sensitivity Heatmap (%)",
        title_font_size=16,
        margin=dict(t=50, b=40, l=10, r=10),
        height=380,
    )
    fig_irr.update_traces(textfont_size=13)
    st.plotly_chart(fig_irr, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("Equity Multiple Sensitivity — Construction Cost × Exit Cap Rate")
    st.caption("Each cell shows equity multiple. Construction cost moves shown at $50K increments.")

    cost_scenarios = {
        "Cost −$100K": construction_cost - 100000,
        "Cost −$50K":  construction_cost - 50000,
        "Base Cost":    construction_cost,
        "Cost +$50K":  construction_cost + 50000,
        "Cost +$100K": construction_cost + 100000,
    }

    em_matrix = []
    for cost_val in cost_scenarios.values():
        row = []
        for cap_val in cap_scenarios.values():
            adj_dev  = development_model.calculate(land_cost, cost_val, soft_cost_rate, units)
            adj_exit = noi / max(cap_val, 0.001)
            adj_inv  = investment_model.calculate(
                adj_dev.total_cost,
                cashflow.yearly_noi,
                adj_exit,
                0.08
            )
            row.append(round(adj_inv["equity_multiple"], 2))
        em_matrix.append(row)

    df_em = pd.DataFrame(
        em_matrix,
        index=list(cost_scenarios.keys()),
        columns=list(cap_scenarios.keys()),
    )

    fig_em = px.imshow(
        df_em,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        zmin=0.5,
        zmax=max(3.0, df_em.values.max()),
        labels=dict(x="Exit Cap Rate Scenario", y="Construction Cost Scenario", color="Equity Multiple"),
    )
    fig_em.update_layout(
        title="Equity Multiple Sensitivity Heatmap",
        title_font_size=16,
        margin=dict(t=50, b=40, l=10, r=10),
        height=380,
    )
    fig_em.update_traces(textfont_size=13)
    st.plotly_chart(fig_em, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — CASH FLOWS
# ═════════════════════════════════════════════════════════════════════════════
with tab_cashflow:

    st.subheader("Projected Annual Cash Flows")

    years = list(range(1, len(cashflow.yearly_noi) + 1))
    df_cf = pd.DataFrame({
        "Year": years,
        "Annual NOI ($)": [round(v) for v in cashflow.yearly_noi],
    })

    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=df_cf["Year"],
        y=df_cf["Annual NOI ($)"],
        marker_color=["#1f4e79" if v >= 0 else "#b34a4a" for v in df_cf["Annual NOI ($)"]],
        hovertemplate="Year %{x}: $%{y:,.0f}<extra></extra>",
    ))
    fig_cf.update_layout(
        xaxis_title="Year",
        yaxis_title="NOI ($)",
        height=360,
        margin=dict(t=20, b=40, l=10, r=10),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"),
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    df_cf["Cumulative NOI ($)"] = df_cf["Annual NOI ($)"].cumsum()
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=df_cf["Year"],
        y=df_cf["Cumulative NOI ($)"],
        mode="lines+markers",
        line=dict(color="#1f4e79", width=2),
        marker=dict(size=7),
        hovertemplate="Year %{x}: $%{y:,.0f}<extra></extra>",
    ))
    fig_cum.update_layout(
        title="Cumulative NOI over Hold Period",
        xaxis_title="Year",
        yaxis_title="Cumulative NOI ($)",
        height=300,
        margin=dict(t=40, b=40, l=10, r=10),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"),
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.dataframe(
        df_cf.style.format({
            "Annual NOI ($)": "${:,.0f}",
            "Cumulative NOI ($)": "${:,.0f}"
        }),
        use_container_width=True,
        hide_index=True,
    )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_analysis:

    st.subheader("Investment Analysis Report")

    market_condition = (
        "favorable"   if market["market_score"] > 0.6 else
        "moderate"    if market["market_score"] > 0.4 else
        "challenging"
    )
    gross_profit = valuation.property_value - development.total_cost

    analysis_html = f"""
    <div class="analysis-section">

    <h3>1. Project Definition & Assumptions</h3>
    <p>This feasibility model evaluates a <span class="highlight">{units}-unit</span> residential
    development in the New York City market. Key input definitions:</p>
    <p>• <span class="highlight">Construction Cost per Unit</span>: ${construction_cost:,}
    — <em>excludes land cost</em>, covering hard construction only. NYC/NJ rental construction
    typically ranges from $400K to $1M+ per unit depending on building class.</p>
    <p>• <span class="highlight">Land Cost</span>: ${land_cost:,} — calculated separately as it is
    highly location-dependent.</p>
    <p>• <span class="highlight">Soft Cost Rate</span>: {soft_cost_rate:.0%} of hard construction
    cost — covers architectural, engineering, legal, permitting, and financing fees.</p>
    <p>• <span class="highlight">Exit Cap Rate</span>: {cap_rate:.2%} — capitalization rate applied
    to stabilized NOI to derive exit property value.</p>

    <h3>2. Income & Operating Expenses</h3>
    <p>Assuming a monthly rent of <span class="highlight">${rent:,}</span> per unit and a vacancy
    rate of {vacancy_rate:.2%}, the effective gross income is
    <span class="highlight">${income.effective_gross_income:,.0f}</span>.</p>
    <p>Operating expenses total <span class="highlight">${expenses.total_expenses:,.0f}</span>,
    which include property taxes (1.2% of EGI), property insurance ($800/unit/year), maintenance
    ($1,200/unit/year), utilities ($900/unit/year), and management fee (5% of EGI). Stabilized
    <span class="highlight">NOI = ${noi:,.0f}</span>.</p>
    <p class="note">Note: NOI is the numerator in cap-rate-based valuation and is, by convention,
    unlevered — debt service (loan costs) is intentionally excluded.</p>

    <h3>3. Valuation & Development Cost</h3>
    <p>Applying the exit cap rate of {cap_rate:.2%} to stabilized NOI yields a projected property
    value of <span class="highlight">${valuation.property_value:,.0f}</span>.</p>
    <p>Total development cost breakdown:</p>
    <p>• Land: ${land_cost:,.0f}<br>
    • Hard construction: ${construction_cost * units:,.0f} ({units} units × ${construction_cost:,})<br>
    • Soft costs: ${construction_cost * units * soft_cost_rate:,.0f} ({soft_cost_rate:.0%} of hard cost)<br>
    • <span class="highlight">Total: ${development.total_cost:,.0f}</span></p>
    <p>Implied <span class="highlight">gross developer profit = ${gross_profit:,.0f}</span>.</p>

    <h3>4. Return Metrics</h3>
    <p>Over a {construction_years}-year construction period, {lease_up_years}-year lease-up, and
    {hold_years}-year hold period, the model yields:</p>
    <p>• <span class="highlight">IRR: {investment['irr']:.2%}</span><br>
    • <span class="highlight">Equity Multiple: {investment['equity_multiple']:.2f}x</span><br>
    • <span class="highlight">NPV (at 8% discount rate): ${investment.get('npv', 0):,.0f}</span></p>
    <p class="note">Note: Returns are reported on a Gross basis — transaction costs at exit (legal
    fees, broker commissions, transfer taxes) are not deducted, as these vary widely by deal
    complexity and are difficult to estimate at the modeling stage.</p>

    <h3>5. Market Context</h3>
    <p>Current NYC market data:</p>
    <p>• Vacancy Rate: {vacancy_rate:.2%}<br>
    • Annual Rent Growth: {rent_growth:.2%}<br>
    • Rental Inventory: {inventory:,} units<br>
    • Discount Share: {discount_rate:.2%}</p>
    <p>The composite market score of <span class="highlight">{market['market_score']:.2f}</span>
    (out of 1.0) reflects <span class="highlight">{market_condition}</span> market conditions.</p>

    <h3>6. Sensitivity</h3>
    <p>IRR is highly sensitive to exit cap rate. A 25–50 basis point move in cap rate produces
    meaningful changes in exit value and equity multiple. The Sensitivity tab shows IRR across a
    ±100 bp cap rate range and ±10% rent range, capturing realistic market volatility.</p>

    <h3>7. Investment Decision</h3>
    <p>Based on the combined return profile and market score, the model recommends:
    <span class="highlight">{decision['decision']}</span>.</p>
    <p>Investors should closely monitor exit cap rate movement (the single largest driver of return),
    construction cost inflation, and NYC regulatory changes — including rent stabilization policies —
    which are not directly captured in this model.</p>

    </div>
    """

    st.markdown(analysis_html, unsafe_allow_html=True)