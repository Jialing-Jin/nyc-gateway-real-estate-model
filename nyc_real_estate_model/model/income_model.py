from dataclasses import dataclass


@dataclass
class IncomeResult:
    gross_rental_income: float
    other_income: float
    effective_gross_income: float
    occupancy_rate: float


class IncomeModel:

    def calculate(
        self,
        units: int,
        avg_monthly_rent: float,
        vacancy_rate: float,
        other_income_per_unit_month: float
    ):

        occupancy_rate = 1 - vacancy_rate

        gross_rental_income = avg_monthly_rent * units * 12

        other_income = other_income_per_unit_month * units * 12

        effective_gross_income = (gross_rental_income + other_income) * occupancy_rate

        return IncomeResult(
            gross_rental_income=gross_rental_income,
            other_income=other_income,
            effective_gross_income=effective_gross_income,
            occupancy_rate=occupancy_rate
        )