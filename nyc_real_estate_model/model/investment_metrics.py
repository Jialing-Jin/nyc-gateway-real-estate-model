import numpy as np
import numpy_financial as npf


class InvestmentMetrics:

    def calculate(self, development_cost, yearly_noi, exit_value, discount_rate):

        cash_flows = [-development_cost]

        for noi in yearly_noi:
            cash_flows.append(noi)

        cash_flows[-1] += exit_value

        irr = npf.irr(cash_flows)

        npv = npf.npv(discount_rate, cash_flows)

        equity_multiple = sum(cash_flows[1:]) / development_cost

        return {
            "cash_flows": cash_flows,
            "irr": irr,
            "npv": npv,
            "equity_multiple": equity_multiple
        }