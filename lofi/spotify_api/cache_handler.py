from __future__ import annotations

import spotipy  # type: ignore

from .. import db
from .token import Token


class CacheHandler(spotipy.cache_handler.CacheHandler):  # type: ignore
    """Cache and retrieve Spotify API tokens in database."""

    def __init__(self, user_id: str, session: db.Session) -> None:
        self.user_id = user_id
        self.session = session
        self.save_token_to_db: bool = True
        self.token_cache: dict[str, str | int] | None = None

    def get_cached_token(self: CacheHandler) -> dict[str, str | int] | None:
        """Return token from database."""
        if self.save_token_to_db:
            user = self.get_user()
            if user.token is None:
                return None
            return Token.model_validate_json(user.token).model_dump()
        return self.token_cache

    def get_user(self) -> db.User:
        """Get User object from database."""
        if (user := self.session.get(db.User, self.user_id)) is None:
            user = db.User(id=self.user_id)
            self.session.add(user)
        return user

    def save_token_to_cache(
        self: CacheHandler, token_info: dict[str, str | int]
    ) -> None:
        """Save token to database."""
        if self.save_token_to_db:
            user = self.get_user()
            user.token = Token.model_validate(token_info).model_dump_json()
        else:
            self.token_cache = token_info
