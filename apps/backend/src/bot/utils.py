from decimal import Decimal, InvalidOperation


def normalize_text(text: str | None) -> str:
    return text.strip() if text else ""


def parse_bool(value: str | None) -> bool | None:
    normalized = normalize_text(value).lower()
    if normalized in {"да", "д", "yes", "y", "true", "1"}:
        return True
    if normalized in {"нет", "н", "no", "false", "0"}:
        return False
    return None


def parse_decimal(text: str | None) -> Decimal | None:
    normalized = normalize_text(text).replace(",", ".")
    if not normalized:
        return None
    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def parse_shared_user_id(raw_value: str | None) -> int | None:
    normalized = normalize_text(raw_value)
    if "(" not in normalized or not normalized.endswith(")"):
        return None
    candidate = normalized.rsplit("(", 1)[1][:-1]
    if not candidate.isdigit():
        return None
    return int(candidate)
