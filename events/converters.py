from uuid import UUID

from base58 import b58decode, b58encode


class ShortUUID:
    """ShortUUID is an extension of the default UUID converter that prefers a
    shorter 22-character url-safe base58 encoding. It's backwards compatible
    with the default UUID converter.
    """

    UUID_36_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    UUID_22_REGEX = r"[0-9A-Za-z]{22}"

    regex = f"({UUID_22_REGEX}|{UUID_36_REGEX})"

    def to_python(self, value: str) -> UUID:
        if len(value) == 22:
            return UUID(bytes=b58decode(value.lstrip("0").encode("utf-8")))
        if len(value) == 36:
            return UUID(value)
        raise ValueError(f"Invalid UUID: {value}")

    def to_url(self, value: UUID) -> str:
        return b58encode(value.bytes).decode("utf-8").zfill(22)
