import pytest
from covidmx import CovidMX


def test_makes_plot():
    try:
        dge_plot = CovidMX().get_plot()
        for st in dge_plot.available_status:
            file_name = '{}.png'.format(st)
            mx_map = dge_plot.plot_map(status=st, save_file_name=file_name)
            mx_map_with_muns = dge_plot.plot_map(status=st, add_municipalities=True, save_file_name=file_name)
            cdmx_map = dge_plot.plot_map(status=st, state='CIUDAD DE MÉXICO', save_file_name=file_name)
            cdmx_map_with_muns = dge_plot.plot_map(status=st, state='CIUDAD DE MÉXICO', add_municipalities=True, save_file_name=file_name)

        dge_plot_historical = CovidMX(date='04-12-2020', date_format='%m-%d-%Y').get_plot()
        for st in dge_plot_historical.available_status:
            mx_map_h = dge_plot_historical.plot_map(status=st, save_file_name=file_name)
            mx_map_with_muns_h = dge_plot_historical.plot_map(status=st, add_municipalities=True, save_file_name=file_name)
            cdmx_map_h = dge_plot_historical.plot_map(status=st, state='CIUDAD DE MÉXICO', save_file_name=file_name)
            cdmx_map_with_muns_h = dge_plot_historical.plot_map(status=st, state='CIUDAD DE MÉXICO', add_municipalities=True, save_file_name=file_name)
    except BaseException:
        assert False, "Test DGEPlot failed"
