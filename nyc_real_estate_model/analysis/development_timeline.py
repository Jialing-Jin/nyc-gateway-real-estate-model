from dataclasses import dataclass


@dataclass
class TimelineResult:
    construction_years: int
    lease_up_years: int
    hold_years: int
    total_years: int
    occupancy_curve: list


class DevelopmentTimeline:

    def build_timeline(
        self,
        construction_years: int,
        lease_up_years: int,
        hold_years: int
    ) -> TimelineResult:

        occupancy_curve = []

        for _ in range(construction_years):
            occupancy_curve.append(0.0)

        if lease_up_years == 1:
            occupancy_curve.append(0.6)
        elif lease_up_years == 2:
            occupancy_curve.extend([0.4, 0.8])
        elif lease_up_years == 3:
            occupancy_curve.extend([0.3, 0.6, 0.9])
        else:
            for i in range(lease_up_years):
                occupancy_curve.append((i + 1) / lease_up_years)

        stabilized_years = hold_years - construction_years - lease_up_years

        for _ in range(max(stabilized_years, 0)):
            occupancy_curve.append(0.95)

        total_years = len(occupancy_curve)

        return TimelineResult(
            construction_years=construction_years,
            lease_up_years=lease_up_years,
            hold_years=hold_years,
            total_years=total_years,
            occupancy_curve=occupancy_curve
        )