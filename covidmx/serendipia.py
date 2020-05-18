import pandas as pd
from itertools import product
from unidecode import unidecode
from covidmx.utils import translate_serendipia
pd.options.mode.chained_assignment = None


class Serendipia:

    def __init__(
            self,
            date=None,
            kind=None,
            clean=True,
            add_search_date=True,
            date_format='%d-%m-%Y'):
        """
        Returns COVID19 data from serendipia.

        Parameters
        ----------
        date: str or list
            Date to consider. If not present returns last found data.
        kind: str
            Kind of data. Allowed: 'confirmados', 'sospechosos'. If not present returns both.
        clean: boolean
            If data cleaning will be performed. Default True (recommended).
        add_search_date: boolean
            If add date to the DFs.
        date_format: str
            date format if needed
        """

        self.allowed_kinds = translate_serendipia

        if not (isinstance(date, str) or date is None):
            raise ValueError('date must be string')

        if not (isinstance(kind, str) or kind is None):
            raise ValueError('kind must be string')

        self.date = date

        if not self.date:
            self.search_date = True
        else:
            self.search_date = False

        if not kind:
            self.kind = self.allowed_kinds
        else:
            assert kind in self.allowed_kinds.keys(), 'Serendipia source only considers {}. Please use one of them.'.format(
                ', '.join(self.allowed_kinds.keys()))

            self.kind = [kind]

        self.clean = clean
        self.add_search_date = add_search_date
        self.date_format = date_format

    def get_data(self):

        print('Reading data')
        dfs = [
            self.read_data(
                dt, ki) for dt, ki in product(
                [self.date], self.kind)]

        if self.clean:
            print('Cleaning data')
            dfs = [self.clean_data(df) for df in dfs]

        dfs = pd.concat(dfs, sort=True).reset_index(drop=True)

        return dfs

    def read_data(self, date, kind):

        if self.search_date:
            df, found_date = self.search_data(5, kind)

            if self.add_search_date:
                df.loc[:, 'fecha_busqueda'] = found_date

            return df

        url = self.get_url(date, kind)

        try:
            df = pd.read_csv(url)

            if self.add_search_date:
                df.loc[:, 'fecha_busqueda'] = date

            return df
        except BaseException:
            raise RuntimeError(
                'Cannot read the data. Maybe theres no information for {} and {}'.format(
                    kind, date))

    def search_data(self, max_times, kind):
        print('Searching last date available for {}...'.format(kind))

        search_dates = pd.date_range(
            end=pd.to_datetime('today'),
            periods=max_times)[::-1]

        for date in search_dates:
            date_formatted = date.strftime(self.date_format)
            url = self.get_url(date_formatted, kind)
            try:
                df = pd.read_csv(url)
                print('Last date available: {}'.format(date_formatted))
                return df, date_formatted
            except BaseException:
                continue

        raise RuntimeError('No date found for {}'.format(kind))

    def clean_data(self, df):

        df.columns = df.columns.str.lower().str.replace(
            ' |-|\n', '_').str.replace('°', '').map(unidecode)

        if [i for i in list(df.columns) if i.startswith('identificac')]:
            df.columns = df.columns.str.replace(r'(?<=identificacion)(\w+)', '')

        # Removing Fuente row
        if [i for i in list(df.columns) if i.startswith('n_caso')]:
            df = df[~df['n_caso'].str.contains('Fuente|Corte')]

        # converting to datetime format
        df.loc[:, 'fecha_busqueda'] = pd.to_datetime(
            df['fecha_busqueda'], format=self.date_format)

        if [i for i in list(df.columns) if i.startswith('fecha_de_inicio')]:
            df.loc[:, 'fecha_de_inicio_de_sintomas'] = pd.to_datetime(
                df['fecha_de_inicio_de_sintomas'], format='%d/%m/%Y')

        return df

    def get_url(self, date, kind):
        """
        Returns the url of serendipia.

        Parameters
        ----------
        date: str
            String date.
        kind: str
            String with kind of data. Allowed: 'positivos', 'sospechosos'
        """
        date_ts = pd.to_datetime(date, format=self.date_format)
        year = date_ts.strftime('%Y')
        month = date_ts.strftime('%m')
        date_f = date_ts.strftime('%Y.%m.%d')

        serendipia_change = pd.to_datetime('19-04-2020', format=self.date_format)

        spec_kind = self.allowed_kinds[kind]

        if spec_kind == 'positivos':
            if date_ts >= serendipia_change:
                date_f = date_ts.strftime('%d%m%Y')
                url = 'https://serendipia.digital/wp-content/uploads/{}/{}/covid-19-mexico-{}.csv'.format(year, month, date_f)
            else:
                url = 'https://serendipia.digital/wp-content/uploads/{}/{}/Tabla_casos_{}_COVID-19_resultado_InDRE_{}-Table-1.csv'.format(year, month, spec_kind, date_f)
        else:
            if date_ts >= serendipia_change:
                date_f = date_ts.strftime('%d%m%Y')
                url = 'https://serendipia.digital/wp-content/uploads/{}/{}/covid-19-mexico-{}-{}.csv'.format(year, month, spec_kind, date_f)
            else:
                url = 'https://serendipia.digital/wp-content/uploads/{}/{}/Tabla_casos_{}_COVID-19_{}-Table-1.csv'.format(year, month, spec_kind, date_f)

        return url
