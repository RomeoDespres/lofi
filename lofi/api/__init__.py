"""Static REST API."""

from .app import generate_typescript_client
from .data import generate_data


__all__ = ["generate_data", "generate_typescript_client"]
