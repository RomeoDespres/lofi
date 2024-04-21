import pytest

from lofi import db
from lofi.spotify_api.cache_handler import CacheHandler
from lofi.spotify_api.token import Token
from tests.utils import load_data


@pytest.fixture()
def user_without_token(session: db.Session) -> db.User:
    load_data(session, user := db.User(id="1", token=None))
    return user


@pytest.fixture()
def user_with_token(session: db.Session, token: Token) -> db.User:
    load_data(session, user := db.User(id="2", token=token.model_dump_json()))
    return user


@pytest.fixture()
def token() -> Token:
    return Token(
        access_token="foo",  # noqa: S106
        expires_at=1,
        expires_in=2,
        refresh_token="bar",  # noqa: S106
        scope="foobar",
        token_type="token",  # noqa: S106
    )


def test_get_user_creates_user_if_necessary(session: db.Session) -> None:
    cache_handler = CacheHandler(user_id="3", session=session)
    user = cache_handler.get_user()
    assert user.id == "3"
    assert user in session


def test_get_user_returns_existing_user(
    session: db.Session,
    user_without_token: db.User,
) -> None:
    cache_handler = CacheHandler(user_id=user_without_token.id, session=session)
    assert cache_handler.get_user().id == user_without_token.id


def test_get_cached_token_returns_none(session: db.Session, user_without_token: db.User, token: Token) -> None:  # noqa: ARG001
    cache_handler = CacheHandler(user_id=user_without_token.id, session=session)
    assert cache_handler.get_cached_token() is None


def test_get_cached_token_returns_correct_token(
    session: db.Session,
    user_with_token: db.User,
    token: Token,
) -> None:
    cache_handler = CacheHandler(user_id=user_with_token.id, session=session)
    assert cache_handler.get_cached_token() == token.model_dump()


def test_save_token_updates_database(
    session: db.Session,
    user_without_token: db.User,
    token: Token,
) -> None:
    assert user_without_token.token is None
    cache_handler = CacheHandler(user_id=user_without_token.id, session=session)
    cache_handler.save_token_to_cache(token.model_dump())
    assert user_without_token.token == token.model_dump_json()


def test_get_cached_token_uses_memory_cache_when_save_to_db_is_false(
    session: db.Session,
    user_without_token: db.User,
    token: Token,
) -> None:
    cache_handler = CacheHandler(user_id=user_without_token.id, session=session)
    assert cache_handler.token_cache is None
    cache_handler.save_token_to_db = False
    cache_handler.save_token_to_cache(token.model_dump())
    assert cache_handler.token_cache == token.model_dump()
    assert cache_handler.get_cached_token() == token.model_dump()
