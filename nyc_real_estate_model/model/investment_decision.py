class InvestmentDecision:

    def decide(
        self,
        irr,
        equity_multiple,
        market_score
    ):

        if irr >= 0.15 and equity_multiple >= 2 and market_score >= 0.6:
            decision = "Invest"

        elif irr >= 0.10 and market_score >= 0.5:
            decision = "Hold"

        else:
            decision = "Reject"

        return {
            "decision": decision
        }