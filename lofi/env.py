"""Defines and loads required configuration for the project."""

from typing import Type, TypeVar, cast, overload

from decouple import UndefinedValueError, config  # type: ignore


__all__ = [
    "AWS_ACCESS_KEY_ID",
    "AWS_DEFAULT_REGION",
    "AWS_SECRET_ACCESS_KEY",
    "UndefinedValueError",
    "env_var",
]


_T = TypeVar("_T")


@overload
def env_var(name: str) -> str:
    ...


@overload
def env_var(name: str, type_: Type[_T]) -> _T:
    ...


def env_var(name: str, type_: Type[_T] | Type[str] = str) -> _T | str:
    """Load variable from environment or .env file.

    Parameters
    ----------
    name : str
        Environement variable or .env entry name.
    type_ : type
        Python type the raw value will be cast to.

    Returns
    -------
    Env var value casted to `type_`.

    Examples
    --------
    ```python
    MY_SECRET_PASSWORD = _env_var("MY_SECRET_PASSWORD", type_=str)
    ```
    """
    return cast(_T, config(name, cast=type_))


AWS_ACCESS_KEY_ID = env_var("AWS_ACCESS_KEY_ID")
AWS_DEFAULT_REGION = env_var("AWS_DEFAULT_REGION")
AWS_SECRET_ACCESS_KEY = env_var("AWS_SECRET_ACCESS_KEY")
