from dataclasses import dataclass


@dataclass
class DevelopmentCostResult:
    land_cost: float
    construction_cost: float
    soft_cost: float
    total_cost: float


class DevelopmentCostModel:

    def calculate(
        self,
        land_cost: float,
        construction_cost_per_unit: float,
        soft_cost_rate: float,
        units: int
    ):

        construction_cost = construction_cost_per_unit * units

        soft_cost = construction_cost * soft_cost_rate

        total_cost = land_cost + construction_cost + soft_cost

        return DevelopmentCostResult(
            land_cost=land_cost,
            construction_cost=construction_cost,
            soft_cost=soft_cost,
            total_cost=total_cost
        )