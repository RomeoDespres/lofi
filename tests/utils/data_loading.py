import functools
from typing import Callable, Concatenate, ParamSpec, Protocol, Sequence, TypeVar

from lofi import db

_B_co = TypeVar("_B_co", db.Base, Sequence[db.Base], covariant=True)
_P = ParamSpec("_P")


class WrappedDataFunction(Protocol[_P, _B_co]):
    def __call__(self, session: db.Session, *args: _P.args, **kwargs: _P.kwargs) -> _B_co: ...


def load_data(session: db.Session, *objs: db.Base) -> None:
    """Load data models into database.

    Parameters
    ----------
    session
        Connected SQLAlchemy session.
    *objs
        SQLAlchemy objects to load.

    """
    session.add_all(objs)
    session.flush()


def load_data_output(
    func: Callable[Concatenate[db.Session, _P], _B_co],
) -> WrappedDataFunction[_P, _B_co]:
    """Wrap a function to load its output into database.

    Parameters
    ----------
    func
        Function having `session` as first argument and returning
        database objects.

    Returns
    -------
    Wrapped function.

    """

    @functools.wraps(func)
    def wrapped(session: db.Session, *args: _P.args, **kwargs: _P.kwargs) -> _B_co:
        output = func(session, *args, **kwargs)
        if isinstance(output, Sequence):
            load_data(session, *output)
        else:
            load_data(session, output)
        return output

    return wrapped
