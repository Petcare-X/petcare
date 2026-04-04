from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PetMeasurementRule:
    label: str
    unit: str
    min_value: Decimal
    max_value: Decimal

    def format_range(self) -> str:
        return f"{_format_decimal(self.min_value)}-{_format_decimal(self.max_value)} {self.unit}"


def _format_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


PET_MEASUREMENT_RULES: dict[str, PetMeasurementRule] = {
    "pet_neck_girth": PetMeasurementRule(
        label="обхват шеи",
        unit="см",
        min_value=Decimal("5"),
        max_value=Decimal("120"),
    ),
    "pet_breast_girth": PetMeasurementRule(
        label="обхват груди",
        unit="см",
        min_value=Decimal("10"),
        max_value=Decimal("200"),
    ),
    "pet_length": PetMeasurementRule(
        label="длина",
        unit="см",
        min_value=Decimal("10"),
        max_value=Decimal("250"),
    ),
    "pet_weight": PetMeasurementRule(
        label="вес",
        unit="кг",
        min_value=Decimal("0.2"),
        max_value=Decimal("200"),
    ),
}


def get_pet_measurement_rule(field_name: str) -> PetMeasurementRule:
    try:
        return PET_MEASUREMENT_RULES[field_name]
    except KeyError as exc:
        raise KeyError(f"Unknown pet measurement field: {field_name}") from exc


def validate_pet_measurement_value(field_name: str, value: Decimal | float | int) -> None:
    rule = get_pet_measurement_rule(field_name)
    decimal_value = Decimal(str(value))
    if decimal_value < rule.min_value or decimal_value > rule.max_value:
        raise ValueError(f"{rule.label.capitalize()} должен быть в диапазоне {rule.format_range()}.")


def validate_pet_measurements_consistency(data: dict[str, Decimal | float | int | None]) -> None:
    neck = data.get("pet_neck_girth")
    breast = data.get("pet_breast_girth")
    if neck is not None and breast is not None and Decimal(str(breast)) < Decimal(str(neck)):
        raise ValueError("Обхват груди не может быть меньше обхвата шеи.")
