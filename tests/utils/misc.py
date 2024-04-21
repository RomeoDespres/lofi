from __future__ import annotations

import functools
from typing import Callable, Iterator, ParamSpec, TypeVar

_T = TypeVar("_T")
_P = ParamSpec("_P")


def iterator_to_list(func: Callable[_P, Iterator[_T]]) -> Callable[_P, list[_T]]:
    """Wrap a function returning an iterator to make it return a list.

    Parameters
    ----------
    func
        The function to wrap.

    Returns
    -------
    Wrapped function

    Examples
    --------
    >>> @iterator_to_list
    ... def f() -> Iterator[int]:
    ...     yield from range(3)
    ...
    >>> f()
    [0, 1, 2]

    """

    @functools.wraps(func)
    def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> list[_T]:
        return list(func(*args, **kwargs))

    return wrapped
