from typing import Callable

from lofi import db
from lofi.spotify_api import SpotifyAPIClient


def get_spotify_api_client_patch(session: db.Session, **kwargs: object) -> Callable[[db.Session], SpotifyAPIClient]:  # noqa: ARG001
    def get_client(session: db.Session) -> SpotifyAPIClient:
        client = SpotifyAPIClient(session, user_id="foo")
        for key, value in kwargs.items():
            setattr(client, key, value)
        return client

    return get_client
