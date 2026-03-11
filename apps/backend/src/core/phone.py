import phonenumbers
from phonenumbers import PhoneNumberFormat

def to_e164(value) -> str:
    pn = getattr(value, "phone_number", None)
    if pn is None:
        pn = value

    if isinstance(pn, str):
        pn = phonenumbers.parse(pn, None)

    return phonenumbers.format_number(pn, PhoneNumberFormat.E164)