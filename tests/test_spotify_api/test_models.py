import datetime

import pytest

from lofi.spotify_api.models import parse_date


@pytest.mark.parametrize("input_str", ["2000-01-01", "2000-01", "2000"])
def test_parse_date_returns_correct_value(input_str: str) -> None:
    assert parse_date(input_str) == datetime.date(2000, 1, 1)


def test_parse_date_raises_on_wrong_input() -> None:
    with pytest.raises(ValueError, match="time data 'foo-01-01' does not match format '%Y-%m-%d'"):
        assert parse_date("foo")
