import pytest
from covidmx import CovidMX


def test_returns_data():
    try:
        covid_data = CovidMX(source='Serendipia').get_data()
        covid_data = CovidMX(source='Serendipia', date='18-04-2020').get_data()
        raw_data = CovidMX(source='Serendipia', clean=False).get_data()
        confirmed = CovidMX(source='Serendipia', kind="confirmed").get_data()
        suspects = CovidMX(source='Serendipia', kind="suspects").get_data()
    except BaseException:
        assert False, "Test Serendipia failed"
