from covidmx.serendipia import Serendipia
from covidmx.dge import DGE


def CovidMX(source="DGE", **kwargs):
    """
    Returns COVID19 data from source.

    Parameters
    ----------
    Args:
        source (str): Source of data. Allowed: DGE, Serendipia.
    Kwargs (source="DGE"):
        clean (bool): Whether data cleaning will be performed. Default True (recommended).
                      Return decoded variables.
        return_catalogo (bool): Whether catalogue of encoding will be returned.
        return_descripcion (bool): Whether a full description of variables will be returned.
        date (str): To get historical data published that date.
        date_format (str): Format of supplied date.
    Kwargs (source="Serendipia"):
        date (str): Date to consider. If not present returns last found data.
        kind (str): Kind of data. Allowed: 'confirmed', 'suspects'. If not present returns both.
        clean (bool): Whether data cleaning will be performed. Default True (recommended).
        add_search_date (bool): Wheter add date to the DFs.
        date_format (str): date format if needed
    """
    allowed_sources = ["DGE", "Serendipia"]

    assert source in allowed_sources, \
        "CovidMX only supports {} as sources".format(', '.join(allowed_sources))

    if source == "DGE":
        return DGE(**kwargs)

    if source == "Serendipia":
        return Serendipia(**kwargs)
