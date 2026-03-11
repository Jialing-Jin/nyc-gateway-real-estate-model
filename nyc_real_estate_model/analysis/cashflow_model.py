from dataclasses import dataclass


@dataclass
class CashFlowResult:
    yearly_noi: list
    stabilized_noi: float


class CashFlowModel:

    def build_cashflow(
        self,
        stabilized_noi: float,
        occupancy_curve: list
    ) -> CashFlowResult:

        yearly_noi = []

        for occ in occupancy_curve:
            yearly_noi.append(stabilized_noi * occ)

        return CashFlowResult(
            yearly_noi=yearly_noi,
            stabilized_noi=stabilized_noi
        )