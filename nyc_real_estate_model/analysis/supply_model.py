class SupplyModel:

    def calculate(self, inventory, inventory_growth):

        supply_pressure = inventory_growth

        elasticity = 0.4

        adjusted_rent_growth = 0.05 - elasticity * supply_pressure

        return {
            "supply_pressure": supply_pressure,
            "adjusted_rent_growth": adjusted_rent_growth
        }