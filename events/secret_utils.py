"""Utility functions for creating and validating "secrets" in this app.
"""
import hashlib
import uuid
from typing import Union

from django.conf import settings


def uuid_to_secret(uuid: Union[str, uuid.UUID]) -> str:
    """Convert a UUID to a secret string. Hashes the id along with the
    SECRET_KEY for the environment.
    """
    sha256 = hashlib.new("sha256")
    sha256.update(str(uuid).encode("utf-8") + settings.SECRET_KEY.encode("utf-8"))
    return sha256.hexdigest()


def secret_is_correct(uuid: Union[str, uuid.UUID], secret: str) -> bool:
    """Validates that the secret string is correct for this givien UUID."""
    return secret == uuid_to_secret(uuid)


class SecretMixin:
    """A mixin for models that have a secret."""

    def secret(self) -> str:
        return uuid_to_secret(self.id)  # type: ignore
