from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass
class Disease:
    """Epidemiological characteristics used to parameterize a model."""

    name: str
    transmission_type: str
    transmission_rate: float
    symptomatic_rate: float | None
    asymptomatic_rate: float | None
    incubation_period: float | None
    infectious_period: float
    latent_period: float
    severity: float | None
    case_fatality_ratio: float | None = None
    infection_fatality_ratio: float | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Disease name must not be empty.")
        if not isinstance(self.transmission_type, str) or not self.transmission_type.strip():
            raise ValueError("Transmission type must not be empty.")

        for field_name in (
            "transmission_rate",
            "infectious_period",
            "latent_period",
        ):
            self._validate_number(getattr(self, field_name), field_name)

        if self.transmission_rate < 0:
            raise ValueError("Transmission rate must be non-negative.")

        for field_name in ("infectious_period", "latent_period"):
            if getattr(self, field_name) <= 0:
                raise ValueError(f"{field_name} must be positive.")

        for field_name in ("incubation_period",):
            value = getattr(self, field_name)
            if value is not None:
                self._validate_number(value, field_name)
                if value <= 0:
                    raise ValueError("incubation_period must be positive.")

        for field_name in (
            "symptomatic_rate",
            "asymptomatic_rate",
            "severity",
            "case_fatality_ratio",
            "infection_fatality_ratio",
        ):
            value = getattr(self, field_name)
            if value is not None:
                self._validate_number(value, field_name)
                if not 0 <= value <= 1:
                    raise ValueError(f"{field_name} must be between 0 and 1.")

    @staticmethod
    def _validate_number(value: object, field_name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{field_name} must be a finite number.")
        if not isfinite(value):
            raise ValueError(f"{field_name} must be a finite number.")