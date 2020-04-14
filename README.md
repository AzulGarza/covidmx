[![Build](https://github.com/FedericoGarza/covidmx/workflows/Python%20package/badge.svg?branch=master)](https://github.com/FedericoGarza/covidmx/tree/master)
[![PyPI version fury.io](https://badge.fury.io/py/covidmx.svg)](https://pypi.python.org/pypi/covidmx/)
[![Downloads](https://pepy.tech/badge/covidmx)](https://pepy.tech/project/covidmx)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/FedericoGarza/covidmx/blob/master/LICENSE)

# covidmx
Python API to get information about COVID-19 in México.

# Requirements

```
python>=3.7
```

# How to install

```
pip install covidmx
```

# How to use

## Direncción General de Epidemiología

The mexican *Dirección General de Epidemiología* [has released open data](https://www.gob.mx/salud/documentos/datos-abiertos-152127) about COVID-19 in México. This source contains information at the individual level such as gender, municipality and health status (smoker, obesity, etc). The package `covidmx` now can handle this source as default. Some variables are encoded as integers and the source also includes a data dictionary with all relevant information. When you pass `clean=True` (default option) returns the decoded data. You can also have access to the catalogue using `return_catalogo=True` and to the description of each one of the variables with `return_descripcion=True`. When you use some of this parameters, the API returns a tuple.

```python
from covidmx import CovidMX

covid_dge_data = CovidMX().get_data()
raw_dge_data = CovidMX(clean=False).get_data()
covid_dge_data, catalogo_data = CovidMX(return_catalogo=True).get_data()
covid_dge_data, descripcion_data = CovidMX(return_descripcion=True).get_data()
covid_dge_data, catalogo_data, descripcion_data = CovidMX(return_catalogo=True, return_descripcion=True).get_data()
```

## Serendipia

Serendipia [publishes daily information](https://serendipia.digital/2020/03/datos-abiertos-sobre-casos-de-coronavirus-covid-19-en-mexico/) of the mexican *Secretaría de Salud* about covid in open format (.csv). This api downloads this data easily, making it useful for task automation.

```python
from covidmx import CovidMX

latest_published_data = CovidMX(source='Serendipia').get_data()
```

By default `CovidMX` instances a `Serendipia` class, searches the latest published data for both confirmed and suspects individuals and finally clean the data. Nevertheless, a more specific search can be conducted (see docs for details).

```python
raw_data = CovidMX(clean=False).get_data()
confirmed = CovidMX(kind="confirmed").get_data()
suspects = CovidMX(kind="suspects").get_data()
particular_published_date = CovidMX(date='2020-04-10', date_format='%Y-%m-%d').get_data()
```
