class MarketScore:

    def calculate(
        self,
        rent_growth,
        vacancy_rate,
        inventory_growth,
        discount_rate
    ):

        rent_weight = 0.35
        vacancy_weight = 0.25
        supply_weight = 0.20
        discount_weight = 0.20

        rent_score = min(max(rent_growth / 0.08, 0), 1)

        vacancy_score = 1 - min(max(vacancy_rate / 0.10, 0), 1)

        supply_score = 1 - min(max(inventory_growth / 0.05, 0), 1)

        discount_score = 1 - min(max(discount_rate / 0.12, 0), 1)

        market_score = (
            rent_score * rent_weight
            + vacancy_score * vacancy_weight
            + supply_score * supply_weight
            + discount_score * discount_weight
        )

        return {
            "rent_score": rent_score,
            "vacancy_score": vacancy_score,
            "supply_score": supply_score,
            "discount_score": discount_score,
            "market_score": market_score
        }