import pytest
from covidmx import CovidMX


def test_returns_data():
    try:
        covid_data = CovidMX().get_data()
    except BaseException:
        assert False, "Test failed"
