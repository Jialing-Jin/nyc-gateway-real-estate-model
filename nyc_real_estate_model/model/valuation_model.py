from dataclasses import dataclass


@dataclass
class ValuationResult:
    cap_rate: float
    property_value: float


class ValuationModel:

    def calculate(self, noi: float, cap_rate: float):

        property_value = noi / cap_rate

        return ValuationResult(
            cap_rate=cap_rate,
            property_value=property_value
        )