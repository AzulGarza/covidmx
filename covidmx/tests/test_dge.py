import pytest
from covidmx import CovidMX


def test_returns_data():
    try:
        covid_dge_data = CovidMX().get_data()
        raw_dge_data = CovidMX(clean=False).get_data()
        covid_dge_data, catalogo_data = CovidMX(return_catalogo=True).get_data()
        covid_dge_data, descripcion_data = CovidMX(return_descripcion=True).get_data()
        covid_dge_data, catalogo_data, descripcion_data = CovidMX(return_catalogo=True, return_descripcion=True).get_data()

        historical_date = CovidMX(clean=False, date='04-12-2020', date_format='%m-%d-%Y').get_data()
        historical_date_1 = CovidMX(date='2020-04-12', date_format='%Y-%m-%d').get_data()
        historical_date_2 = CovidMX(clean=False, date='12-04-2020').get_data()
    except BaseException:
        assert False, "Test DGE failed"
