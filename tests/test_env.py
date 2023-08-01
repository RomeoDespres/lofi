import os
import pytest

from lofi.env import UndefinedValueError, env_var


@pytest.fixture
def temp_env_var(monkeypatch: pytest.MonkeyPatch) -> tuple[str, int]:
    assert "FOO" not in os.environ
    name, value = "FOO", 123
    monkeypatch.setenv(name, str(value))
    return name, value


def test_env_var_raises_error_if_config_is_not_set() -> None:
    assert "FOO" not in os.environ
    with pytest.raises(UndefinedValueError):
        env_var("FOO")


def test_env_var_casts_to_input_type(temp_env_var: tuple[str, int]) -> None:
    var = env_var(temp_env_var[0], int)
    assert isinstance(var, int)
    assert var == temp_env_var[1]


def test_env_var_returns_string_by_default(temp_env_var: tuple[str, int]) -> None:
    var = env_var(temp_env_var[0])
    assert isinstance(var, str)
