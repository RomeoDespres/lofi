from __future__ import annotations

import itertools

import pytest

from lofi.spotify_api.tracklist_utils import InvertibleList, get_tracklist_reorders


@pytest.mark.parametrize(
    ("input_list", "start", "length"),
    [(list(range(n)), i, length) for n in range(8) for i in range(n) for length in range(n - i)],
)
def test_delete_from_invertible_list(input_list: list[int], start: int, length: int) -> None:
    il = InvertibleList(input_list)
    il.delete(start, length)
    del input_list[start : start + length]
    assert list(il) == input_list
    for val in input_list:
        assert il.index(val) == input_list.index(val)


@pytest.mark.parametrize(
    ("input_list", "start", "values"),
    [(list(range(n)), i, list(range(n, n + m))) for n in range(8) for i in range(n) for m in range(n)],
)
def test_insert_into_invertible_list(input_list: list[int], start: int, values: list[int]) -> None:
    il = InvertibleList(input_list)
    il.insert(start, values)
    input_list = input_list[:start] + values + input_list[start:]
    assert list(il) == input_list
    for val in input_list:
        assert il.index(val) == input_list.index(val)


@pytest.mark.parametrize(
    ("current", "target"),
    [(list(permutation), list(range(n))) for n in range(5) for permutation in itertools.permutations(list(range(n)))],
)
def test_get_tracklist_reorders(current: list[int], target: list[int]) -> None:
    for reorder in get_tracklist_reorders(target, current):
        moved_indexes = slice(reorder.range_start, reorder.range_start + reorder.range_length)
        moved_items = current[moved_indexes]
        del current[moved_indexes]
        current = current[: reorder.insert_before] + moved_items + current[reorder.insert_before :]
    assert target == current
