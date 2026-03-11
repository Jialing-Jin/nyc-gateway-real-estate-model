from nyc_real_estate_model.utils.rent_loader import get_latest_nyc_rent
from nyc_real_estate_model.utils.vacancy_loader import get_latest_vacancy
from nyc_real_estate_model.utils.inventory_loader import get_latest_inventory
from nyc_real_estate_model.utils.discount_loader import get_latest_discount

from nyc_real_estate_model.analysis.rent_growth import get_rent_growth
from nyc_real_estate_model.analysis.development_timeline import DevelopmentTimeline
from nyc_real_estate_model.analysis.cashflow_model import CashFlowModel
from nyc_real_estate_model.analysis.supply_model import SupplyModel
from nyc_real_estate_model.analysis.market_score import MarketScore
from nyc_real_estate_model.analysis.sensitivity_analysis import SensitivityAnalysis
from nyc_real_estate_model.analysis.rent_sensitivity import run_rent_sensitivity

from nyc_real_estate_model.model.income_model import IncomeModel
from nyc_real_estate_model.model.expense_model import ExpenseModel
from nyc_real_estate_model.model.valuation_model import ValuationModel
from nyc_real_estate_model.model.development_cost import DevelopmentCostModel
from nyc_real_estate_model.model.investment_metrics import InvestmentMetrics
from nyc_real_estate_model.model.investment_decision import InvestmentDecision


def main():

    units = 100
    avg_monthly_rent = get_latest_nyc_rent("nyc_real_estate_model/data/medianAskingRent_All.csv")
    vacancy_rate = get_latest_vacancy("nyc_real_estate_model/data/NYHVAC.csv")

    inventory = get_latest_inventory("nyc_real_estate_model/data/rentalInventory_All.csv")

    print("NYC Rental Inventory:", inventory)

    discount_rate = get_latest_discount("nyc_real_estate_model/data/discountShare_All.csv")

    print("NYC Discount Rate:", discount_rate)

    construction_years = 2
    lease_up_years = 1
    hold_years = 5

    timeline_model = DevelopmentTimeline()

    timeline_result = timeline_model.build_timeline(
        construction_years=construction_years,
        lease_up_years=lease_up_years,
        hold_years=hold_years
    )

    print("Occupancy Curve:", timeline_result.occupancy_curve)

    other_income_per_unit_month = 50

    income_model = IncomeModel()

    income_result = income_model.calculate(
        units,
        avg_monthly_rent,
        vacancy_rate,
        other_income_per_unit_month
    )

    print("Gross Rental Income:", income_result.gross_rental_income)
    print("Other Income:", income_result.other_income)
    print("Occupancy Rate:", income_result.occupancy_rate)
    print("Effective Gross Income:", income_result.effective_gross_income)

    expense_model = ExpenseModel()

    expense_result = expense_model.calculate(
        effective_gross_income=income_result.effective_gross_income,
        tax_rate=0.012,
        insurance_per_unit=800,
        maintenance_per_unit=1200,
        utilities_per_unit=900,
        management_rate=0.05,
        units=units
    )

    print("Total Expenses:", expense_result.total_expenses)

    noi = income_result.effective_gross_income - expense_result.total_expenses

    print("NOI:", noi)

    cashflow_model = CashFlowModel()

    cashflow_result = cashflow_model.build_cashflow(
        stabilized_noi=noi,
        occupancy_curve=timeline_result.occupancy_curve
    )

    print("Yearly NOI:", cashflow_result.yearly_noi)

    valuation_model = ValuationModel()

    valuation_result = valuation_model.calculate(
        noi=noi,
        cap_rate=0.05
    )

    print("Property Value:", valuation_result.property_value)

    development_model = DevelopmentCostModel()

    development_result = development_model.calculate(
        land_cost=15000000,
        construction_cost_per_unit=350000,
        soft_cost_rate=0.25,
        units=units
    )

    print("Development Cost:", development_result.total_cost)

    profit = valuation_result.property_value - development_result.total_cost

    print("Developer Profit:", profit)

    run_rent_sensitivity()

    growth = get_rent_growth("nyc_real_estate_model/data/medianAskingRent_All.csv")

    future_rent = avg_monthly_rent * (1 + growth)

    print("Rent Growth:", growth)
    print("Future Rent:", future_rent)

    future_noi = future_rent / avg_monthly_rent * noi

    exit_cap_rate = 0.05

    exit_value = future_noi / exit_cap_rate

    exit_score = exit_value / development_result.total_cost

    print("Future NOI:", future_noi)
    print("Exit Value:", exit_value)
    print("Exit Score:", exit_score)

    investment_model = InvestmentMetrics()

    investment_result = investment_model.calculate(
        development_cost=development_result.total_cost,
        yearly_noi=cashflow_result.yearly_noi,
        exit_value=exit_value,
        discount_rate=0.08
    )

    print("Cash Flows:", investment_result["cash_flows"])
    print("IRR:", investment_result["irr"])
    print("NPV:", investment_result["npv"])
    print("Equity Multiple:", investment_result["equity_multiple"])

    inventory_growth = 0.03

    supply_model = SupplyModel()

    supply_result = supply_model.calculate(
        inventory,
        inventory_growth
    )

    print("Supply Pressure:", supply_result["supply_pressure"])
    print("Adjusted Rent Growth:", supply_result["adjusted_rent_growth"])

    inventory_growth = 0.03

    market_model = MarketScore()

    market_result = market_model.calculate(
        rent_growth=growth,
        vacancy_rate=vacancy_rate,
        inventory_growth=inventory_growth,
        discount_rate=discount_rate
    )

    print("Market Score:", market_result["market_score"])

    decision_model = InvestmentDecision()

    decision_result = decision_model.decide(
        irr=investment_result["irr"],
        equity_multiple=investment_result["equity_multiple"],
        market_score=market_result["market_score"]
    )

    print("Investment Decision:", decision_result["decision"])

    sensitivity_model = SensitivityAnalysis()

    sensitivity_results = sensitivity_model.run(
        base_rent=avg_monthly_rent,
        base_cost=development_result.total_cost,
        base_cap_rate=0.05,
        noi=noi,
        development_cost=development_result.total_cost
    )

    for r in sensitivity_results:
        print(r)


if __name__ == "__main__":
    main()