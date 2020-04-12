from covidmx.serendipia import Serendipia


def CovidMX(source="Serendipia", **kwargs):
    """
    DOCS..
    """
    allowed_sources = ["Serendipia"]

    assert source in allowed_sources, \
        "CovidMX only supports {} as sources".format(', '.join(allowed_sources))

    if source == "Serendipia":
        return Serendipia(**kwargs)
