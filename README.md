![Build](https://github.com/FedericoGarza/covidmx/workflows/Python%20package/badge.svg?branch=master)
![Released](https://github.com/FedericoGarza/covidmx/workflows/Python%20package/badge.svg?branch=master&event=release)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# covidmx
Python API to get information about COVID-19 in México.

# Requirements

```
more-itertools>=6.0.0
pandas>=0.25.2
Unidecode>=1.1.1
```

# How to install

```
pip install covidmx
```

# How to use

## Serendipia

Serendipia publishes daily the information of the mexican *Secretaría de Salud* about covid in open format (.csv). This api downloads this data easily, making it useful for task automation.

```python
from covidmx import CovidMX

latest_published_data = CovidMX().get_data()
```

By default `CovidMX` instances a `Serendipia` class, searches the latest published data for both confirmed and suspects individuals and finally clean the data. Nevertheless, a more specific search can be conducted (see docs for details).

```python
raw_data = CovidMX(clean=False).get_data()
confirmed = CovidMX(kind="confirmed").get_data()
suspects = CovidMX(kind="suspects").get_data()
particular_published_date = CovidMX(date='2020-04-10', date_format='%Y-%m-%d').get_data()
```
