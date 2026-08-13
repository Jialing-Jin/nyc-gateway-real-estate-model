import math
from dataclasses import dataclass


@dataclass
class TimelineResult:
    construction_years: int
    lease_up_years: float
    hold_years: int
    total_years: int
    occupancy_curve: list


class DevelopmentTimeline:

    STABILIZED_OCCUPANCY = 0.95

    def build_timeline(
        self,
        construction_years: int,
        lease_up_years: float,
        hold_years: int
    ) -> TimelineResult:

        S = self.STABILIZED_OCCUPANCY
        L = lease_up_years

        occupancy_curve = [0.0] * construction_years

        # Number of annual cash-flow buckets needed to cover the lease-up
        # ramp. A lease-up of 1.5 years needs 2 buckets (year 1 fully
        # inside the ramp, year 2 half ramp / half stabilized).
        num_leaseup_buckets = math.ceil(L) if L > 0 else 0

        for i in range(num_leaseup_buckets):
            occupancy_curve.append(round(self._avg_occupancy(i, i + 1, L, S), 4))

        # Stabilized hold period: hold_years is ADDITIVE — it represents
        # the stabilized years after lease-up completes (per the report:
        # "8 years = 2 construction + 1 lease-up + 5 stabilized hold"),
        # not a total-project-year figure to subtract from.
        for _ in range(hold_years):
            occupancy_curve.append(S)

        total_years = len(occupancy_curve)

        return TimelineResult(
            construction_years=construction_years,
            lease_up_years=lease_up_years,
            hold_years=hold_years,
            total_years=total_years,
            occupancy_curve=occupancy_curve
        )

    @staticmethod
    def _avg_occupancy(a: float, b: float, L: float, S: float) -> float:
        """Average occupancy over year-bucket [a, b) given a linear ramp
        from 0 to S over [0, L], followed by flat occupancy S thereafter."""
        if L <= 0:
            return S
        if b <= L:
            return S * (a + b) / (2 * L)
        if a >= L:
            return S
        ramp_integral = S / L * (L ** 2 - a ** 2) / 2
        stabilized_integral = S * (b - L)
        return ramp_integral + stabilized_integral