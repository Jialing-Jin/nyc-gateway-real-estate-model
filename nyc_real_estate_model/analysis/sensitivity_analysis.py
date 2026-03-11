class SensitivityAnalysis:

    def run(
        self,
        base_rent,
        base_cost,
        base_cap_rate,
        noi,
        development_cost
    ):

        rent_changes = [-0.10, -0.05, 0, 0.05, 0.10]
        cap_changes = [-0.01, -0.005, 0, 0.005, 0.01]
        cost_changes = [-0.10, -0.05, 0, 0.05, 0.10]

        results = []

        for r in rent_changes:

            adjusted_noi = noi * (1 + r)

            value = adjusted_noi / base_cap_rate

            profit = value - development_cost

            results.append({
                "scenario": f"Rent {int(r*100)}%",
                "value": value,
                "profit": profit
            })

        for c in cap_changes:

            adjusted_cap = base_cap_rate + c

            value = noi / adjusted_cap

            profit = value - development_cost

            results.append({
                "scenario": f"Cap Rate {round(c*100,2)}%",
                "value": value,
                "profit": profit
            })

        for k in cost_changes:

            adjusted_cost = development_cost * (1 + k)

            profit = (noi / base_cap_rate) - adjusted_cost

            results.append({
                "scenario": f"Cost {int(k*100)}%",
                "value": noi / base_cap_rate,
                "profit": profit
            })

        return results