from __future__ import annotations

from typing import Generic, Iterator, Sequence, TypeVar, overload

from pydantic import BaseModel

_T = TypeVar("_T")


class InvertibleList(Generic[_T]):
    def __init__(self, values: Sequence[_T] = []) -> None:
        self.values = list(values)
        self.inverted = {val: index for index, val in enumerate(values)}

    @overload
    def __getitem__(self, key: int) -> _T:  # pragma: no cover
        ...

    @overload
    def __getitem__(self, key: slice) -> list[_T]:  # pragma: no cover
        ...

    def __getitem__(self, key: int | slice) -> _T | list[_T]:
        return self.values[key]

    def __iter__(self) -> Iterator[_T]:
        yield from self.values

    def delete(self, start: int, length: int) -> None:
        stop = start + length
        deleted_values = self.values[start:stop]
        del self.values[start:stop]
        for value in deleted_values:
            del self.inverted[value]
        for value in self.values[start:]:
            self.inverted[value] -= stop - start

    def insert(self, start: int, values: Sequence[_T]) -> None:
        self.values = self.values[:start] + list(values) + self.values[start:]
        for i, val in enumerate(values):
            self.inverted[val] = start + i
        for val in self.values[start + len(values) :]:
            self.inverted[val] += len(values)

    def index(self, val: _T) -> int:
        return self.inverted[val]


class TracklistReorder(BaseModel):
    range_start: int
    range_length: int
    insert_before: int


def get_tracklist_reorders(
    target: Sequence[_T],
    current: Sequence[_T],
) -> Iterator[TracklistReorder]:
    target = list(target)
    current = list(current)
    invertible_current = InvertibleList(current)
    max_reorder_length = 100

    def get_next_reorder(insert_before: int) -> TracklistReorder | None:
        if insert_before >= len(current):
            return None
        while insert_before < len(current) and invertible_current[insert_before] == target[insert_before]:
            insert_before += 1
        if insert_before == len(current):
            return None
        start = invertible_current.index(target[insert_before])
        length = 1
        while (
            length <= max_reorder_length
            and (end := (start + length - 1)) < len(target)
            and target[length - 1] == invertible_current[end]
        ):
            length += 1
        if length > 1:
            length -= 1
        return TracklistReorder(
            insert_before=insert_before,
            range_length=length,
            range_start=start,
        )

    insert_before = 0
    while (reorder := get_next_reorder(insert_before)) is not None:
        yield reorder
        insert_before += reorder.range_length
        moved_items = invertible_current[reorder.range_start : reorder.range_start + reorder.range_length]
        invertible_current.delete(reorder.range_start, reorder.range_length)
        invertible_current.insert(reorder.insert_before, moved_items)
    return
