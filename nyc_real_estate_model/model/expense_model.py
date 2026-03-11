from dataclasses import dataclass


@dataclass
class ExpenseResult:
    property_tax: float
    insurance: float
    maintenance: float
    utilities: float
    management_fee: float
    total_expenses: float


class ExpenseModel:

    def calculate(
        self,
        effective_gross_income: float,
        tax_rate: float,
        insurance_per_unit: float,
        maintenance_per_unit: float,
        utilities_per_unit: float,
        management_rate: float,
        units: int
    ):

        property_tax = effective_gross_income * tax_rate

        insurance = insurance_per_unit * units

        maintenance = maintenance_per_unit * units

        utilities = utilities_per_unit * units

        management_fee = effective_gross_income * management_rate

        total_expenses = (
            property_tax +
            insurance +
            maintenance +
            utilities +
            management_fee
        )

        return ExpenseResult(
            property_tax=property_tax,
            insurance=insurance,
            maintenance=maintenance,
            utilities=utilities,
            management_fee=management_fee,
            total_expenses=total_expenses
        )