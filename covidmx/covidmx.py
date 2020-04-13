from covidmx.serendipia import Serendipia


def CovidMX(source="Serendipia", **kwargs):
    """
    Returns COVID19 data from source.

    Parameters
    ----------
    source: str
        Source of data. Allowed: Serendipia.
    date: str or list
        Date to consider. If not present returns last found data.
    kind: str
        Kind of data. Allowed: 'confirmed', 'suspects'. If not present returns both.
    clean: boolean
        If data cleaning will be performed. Default True (recommended).
    add_search_date: boolean
        If add date to the DFs.
    date_format: str
        date format if needed
    """
    allowed_sources = ["Serendipia"]

    assert source in allowed_sources, \
        "CovidMX only supports {} as sources".format(', '.join(allowed_sources))

    if source == "Serendipia":
        return Serendipia(**kwargs)
