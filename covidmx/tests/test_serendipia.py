import pytest
from covidmx import CovidMX


def test_returns_data():
    try:
        covid_data = CovidMX().get_data()
        raw_data = CovidMX(clean=False).get_data()
        confirmed = CovidMX(kind="confirmed").get_data()
        suspects = CovidMX(kind="suspects").get_data()
    except BaseException:
        assert False, "Test failed"
