from io import BytesIO
import requests
from zipfile import ZipFile
import pandas as pd
from itertools import product
from unidecode import unidecode
from covidmx.utils import translate_serendipia
pd.options.mode.chained_assignment = None

URL_DATA = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'
URL_DESCRIPTION = 'http://187.191.75.115/gobmx/salud/datos_abiertos/diccionario_datos_covid19.zip'


class DGE:

    def __init__(
            self,
            clean=True,
            return_catalogo=False,
            return_descripcion=False):
        """
        Returns COVID19 data from the Direccion General de Epidemiología

        """

        self.clean = clean
        self.return_catalogo = return_catalogo
        self.return_descripcion = return_descripcion

    def get_data(self):

        print('Reading data from Direccion General de Epidemiologia...')
        df, catalogo, descripcion = self.read_data()

        if self.clean:
            df = self.clean_data(df)

        if self.return_catalogo and not self.return_descripcion:
            return df, catalogo

        if self.return_descripcion and not self.return_catalogo:
            return df, descripcion

        if self.return_catalogo and self.return_descripcion:
            return df, catalogo, descripcion

        return df

    def read_data(self):
        try:
            data = pd.read_csv(URL_DATA, encoding="ISO-8859-1")
        except BaseException:
            raise RuntimeError('Cannot read the data.')

        try:
            r_url = requests.get(URL_DESCRIPTION, stream=True)
            zip_file = ZipFile(BytesIO(r_url.content))
        except BaseException:
            raise RuntimeError('Cannot read data description.')

        catalogo = pd.ExcelFile(zip_file.open('Catalogos_0412.xlsx'))
        catalogo_original = {sheet: self.parse_catalogo_data(
            sheet, catalogo) for sheet in catalogo.sheet_names}
        catalogo_dict = {
            key.replace(
                'Catálogo ',
                '').replace(
                'de ',
                ''): df for key,
            df in catalogo_original.items()}
        catalogo_dict = {
            key: self.get_dict_replace(
                key,
                df) for key,
            df in catalogo_dict.items()}

        desc = zip_file.open('Descriptores_0412.xlsx')
        desc = pd.read_excel(desc)
        desc_dict = dict(zip(desc['NOMBRE DE VARIABLE'].apply(
            self.clean_nombre_variable), desc['FORMATO O FUENTE'].apply(self.clean_formato_fuente)))

        data['MUNICIPIO_RES'] = data['ENTIDAD_RES'].astype(
            str) + '_' + data['MUNICIPIO_RES'].astype(str)

        for col in data.columns:
            data[col] = self.replace_values(
                data, col, desc_dict, catalogo_dict)

        return data, catalogo_original, desc

    def parse_catalogo_data(self, sheet, excel_file):

        if 'RESULTADO' in sheet:
            return excel_file.parse(sheet, skiprows=1)

        return excel_file.parse(sheet)

    def get_dict_replace(self, key, df):
        if key == 'ENTIDADES':
            return dict(zip(df['CLAVE_ENTIDAD'], df['ENTIDAD_FEDERATIVA']))
        elif key == 'MUNICIPIOS':
            id_mun = df['CLAVE_ENTIDAD'].astype(
                str) + '_' + df['CLAVE_MUNICIPIO'].astype(str)

            return dict(zip(id_mun, df['MUNICIPIO']))

        return dict(zip(df['CLAVE'], df['DESCRIPCIÓN']))

    def clean_formato_fuente(self, formato):
        if 'CATÁLOGO' in formato or 'CATALÓGO' in formato:
            return formato.replace(
                'CATÁLOGO: ',
                '').replace(
                'CATALÓGO: ',
                '').replace(
                ' ',
                '')
        elif 'TEXTO' in formato and '99' in formato:
            return {'99': 'SE IGNORA'}
        elif 'TEXTO' in formato and '97' in formato:
            return {'97': 'NO APLICA'}
        elif 'NUMÉRICA' in formato or 'NÚMERICA' in formato:
            return None
        elif 'AAAA' in formato:
            return formato.replace(
                'AAAA',
                '%Y').replace(
                'MM',
                '%m').replace(
                'DD',
                '%d')

        return formato

    def clean_nombre_variable(self, nombre_variable):

        if 'HABLA_LENGUA' in nombre_variable:
            return 'HABLA_LENGUA_INDI'

        if 'OTRAS_COM' in nombre_variable:
            return 'OTRA_CON'

        return nombre_variable

    def replace_values(self, data, col_name, desc_dict, catalogo_dict):

        formato = desc_dict[col_name]
        if 'FECHA' in col_name:
            return pd.to_datetime(
                data[col_name],
                format=formato,
                errors='coerce')

        if formato is None:
            return data[col_name]

        if isinstance(formato, dict):
            return data[col_name].replace(formato)

        replacement = catalogo_dict[formato]
        return data[col_name].replace(replacement)

    def clean_data(self, df):

        df.columns = df.columns.str.lower()

        return df
