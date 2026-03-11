from nyc_real_estate_model.model.income_model import IncomeModel
from nyc_real_estate_model.model.expense_model import ExpenseModel
from nyc_real_estate_model.model.valuation_model import ValuationModel


def run_rent_sensitivity():

    units = 100
    vacancy_rate = 0.0141
    other_income_per_unit_month = 50

    tax_rate = 0.012
    insurance_per_unit = 800
    maintenance_per_unit = 1200
    utilities_per_unit = 900
    management_rate = 0.05

    cap_rate = 0.05

    income_model = IncomeModel()
    expense_model = ExpenseModel()
    valuation_model = ValuationModel()

    rents = [2600, 2800, 3000, 3200, 3400]

    for rent in rents:

        income = income_model.calculate(
            units,
            rent,
            vacancy_rate,
            other_income_per_unit_month
        )

        expense = expense_model.calculate(
            effective_gross_income=income.effective_gross_income,
            tax_rate=tax_rate,
            insurance_per_unit=insurance_per_unit,
            maintenance_per_unit=maintenance_per_unit,
            utilities_per_unit=utilities_per_unit,
            management_rate=management_rate,
            units=units
        )

        noi = income.effective_gross_income - expense.total_expenses

        valuation = valuation_model.calculate(
            noi=noi,
            cap_rate=cap_rate
        )

        development_cost = 58750000

        profit = valuation.property_value - development_cost

        print("Rent:", rent)
        print("NOI:", noi)
        print("Value:", valuation.property_value)
        print("Profit:", profit)
        print()