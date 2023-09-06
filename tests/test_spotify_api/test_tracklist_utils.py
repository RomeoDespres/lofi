import itertools
import pytest

from lofi.spotify_api.tracklist_utils import InvertibleList, get_tracklist_reorders


@pytest.mark.parametrize(
    ["input", "start", "length"],
    [
        (list(range(n)), i, length)
        for n in range(8)
        for i in range(n)
        for length in range(n - i)
    ],
)
def test_delete_from_invertible_list(input: list[int], start: int, length: int) -> None:
    il = InvertibleList(input)
    il.delete(start, length)
    del input[start : start + length]
    assert list(il) == input
    for val in input:
        assert il.index(val) == input.index(val)


@pytest.mark.parametrize(
    ["input", "start", "values"],
    [
        (list(range(n)), i, list(range(n, n + m)))
        for n in range(8)
        for i in range(n)
        for m in range(n)
    ],
)
def test_insert_into_invertible_list(
    input: list[int], start: int, values: list[int]
) -> None:
    il = InvertibleList(input)
    il.insert(start, values)
    input = input[:start] + values + input[start:]
    assert list(il) == input
    for val in input:
        assert il.index(val) == input.index(val)


@pytest.mark.parametrize(
    ["current", "target"],
    [
        (list(permutation), list(range(n)))
        for n in range(5)
        for permutation in itertools.permutations(list(range(n)))
    ],
)
def test_get_tracklist_reorders(current: list[int], target: list[int]) -> None:
    for reorder in get_tracklist_reorders(target, current):
        range = slice(reorder.range_start, reorder.range_start + reorder.range_length)
        moved_items = current[range]
        del current[range]
        current = (
            current[: reorder.insert_before]
            + moved_items
            + current[reorder.insert_before :]
        )
    assert target == current
