from __future__ import annotations

import abc
import datetime
import random
from typing import Any, Generic, Mapping, Sequence, TypeVar, cast, get_args, get_origin

_D = TypeVar("_D", bound=Mapping[str, Any])
_T = TypeVar("_T")
_U = TypeVar("_U")


class DataGenerator(Generic[_D, _T], abc.ABC):
    def __init__(self) -> None:
        self._id = 0
        self._random = random.Random(self.__class__.__name__)  # noqa: S311

    @classmethod
    def data_class(cls) -> type[_T]:
        for base in cls.__orig_bases__:  # type: ignore[attr-defined]
            if get_origin(base) is DataGenerator:
                return cast(type[_T], get_args(base)[1])
        msg = f"{cls} is not a subclass of DataGenerator."
        raise TypeError(msg)

    @abc.abstractmethod
    def generate_default(self, id_: int) -> _D:
        raise NotImplementedError

    def generate(self, **kwargs: object) -> _T:
        self._id += 1
        return self.data_class()(**{**self.generate_default(self._id), **kwargs})

    def random_bool(self) -> bool:
        return bool(self._random.randint(0, 1))

    def random_choice(self, it: Sequence[_U]) -> _U:
        return self._random.choice(it)

    def random_date(self) -> datetime.date:
        utc = datetime.timezone.utc
        min_date, max_date = datetime.datetime(1900, 1, 1, tzinfo=utc), datetime.datetime(2030, 1, 1, tzinfo=utc)
        delta = int((max_date - min_date).total_seconds())
        return (min_date + datetime.timedelta(seconds=self._random.randrange(delta))).date()

    def random_float(self) -> float:
        return self._random.random()

    def random_permutation(self, it: Sequence[_U]) -> Sequence[_U]:
        return self._random.sample(it, k=len(it))
