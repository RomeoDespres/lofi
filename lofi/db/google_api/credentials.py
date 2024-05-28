from __future__ import annotations

import json
import os
import pathlib
from typing import Any, cast

from google.auth.transport.requests import Request  # type: ignore[import-untyped]
from google.oauth2.credentials import Credentials  # type: ignore[import-untyped]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from pydantic import BaseModel, ValidationError

DEFAULT_API_TOKEN_PATH = pathlib.Path("google_api_token.json")


class _GoogleAPIInstalledAppClientConfig(BaseModel):
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    client_id: str
    client_secret: str
    project_id: str
    redirect_uris: list[str]
    token_uri: str = "https://oauth2.googleapis.com/token"


class _GoogleAPIClientConfig(BaseModel):
    installed: _GoogleAPIInstalledAppClientConfig


def get_google_authorized_user_info(api_token_path: pathlib.Path) -> dict[str, str] | None:
    if api_token_path.exists():
        return cast(dict[str, str], json.loads(api_token_path.read_text("utf8")))
    return None


def get_google_client_config() -> dict[str, Any] | None:
    config_dict = {
        "installed": {
            "client_id": os.getenv("GOOGLE_API_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_API_CLIENT_SECRET"),
            "project_id": os.getenv("GOOGLE_API_PROJECT_ID"),
            "redirect_uris": [os.getenv("GOOGLE_API_REDIRECT_URI")],
        },
    }
    try:
        return _GoogleAPIClientConfig.model_validate(config_dict).model_dump()
    except ValidationError:
        return None


def get_google_credentials(scopes: list[str], api_token_path: pathlib.Path = DEFAULT_API_TOKEN_PATH) -> Credentials:
    credentials: None | Credentials = None

    if (user_info := get_google_authorized_user_info(api_token_path)) is not None:
        credentials = Credentials.from_authorized_user_info(user_info, scopes)

    if credentials is None or not credentials.valid:
        if credentials is not None and credentials.expired and credentials.refresh_token is not None:
            credentials.refresh(Request())

        elif (client_config := get_google_client_config()) is not None:
            # Requires interactive login from user - only used during development
            credentials = get_google_credentials_from_client_config(client_config, scopes)
        else:
            raise_missing_google_credentials(api_token_path)

        assert credentials is not None

        # Cache new token
        api_token_path.write_text(credentials.to_json(), "utf8")

    return credentials


def get_google_credentials_from_client_config(client_config: dict[str, Any], scopes: list[str]) -> Credentials:
    return InstalledAppFlow.from_client_config(client_config, scopes).run_local_server(port=0)


def raise_missing_google_credentials(api_token_path: pathlib.Path) -> None:
    msg = (
        "Missing Google API credentials. Either set all four GOOGLE_API_CLIENT_ID, GOOGLE_API_CLIENT_SECRET, "
        "GOOGLE_API_PROJECT_ID, and GOOGLE_API_REDIRECT_URI environment variables, or store a refresh token in "
        f"{api_token_path}."
    )
    raise RuntimeError(msg)
