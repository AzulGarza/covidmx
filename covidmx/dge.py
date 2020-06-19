from io import BytesIO
import requests
from zipfile import ZipFile
import pandas as pd
from itertools import product
from unidecode import unidecode
from covidmx.utils import translate_serendipia
from covidmx.dge_plot import DGEPlot

pd.options.mode.chained_assignment = None

import wget# import urllib
import os
import zipfile
import shutil 

URL_DATA = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'
URL_DESCRIPTION = 'http://187.191.75.115/gobmx/salud/datos_abiertos/diccionario_datos_covid19.zip'
URL_HISTORICAL = 'http://187.191.75.115/gobmx/salud/datos_abiertos/historicos/datos_abiertos_covid19_{}.zip'


class DGE:

    def __init__(
            self,
            clean=True,
            return_catalogo=False,
            return_descripcion=False,
            date=None,
            date_format='%d-%m-%Y',
            data_path=None):
        """
        Returns COVID19 data from the Direccion General de Epidemiología

        """
        self.clean = clean
        self.return_catalogo = return_catalogo
        self.return_descripcion = return_descripcion
        self.data_path = data_path

        self.date = date
        if date is not None:
            self.date = pd.to_datetime(date, format=date_format)
            assert self.date >= pd.to_datetime('2020-04-12'), 'Historical data only available as of 2020-04-12'

    def get_data(self, preserve_original=None):        
        if not self.data_path is None:
            if not os.path.exists(self.data_path): os.mkdir(self.data_path)
            clean_data_file= os.path.join( self.data_path, os.path.split( URL_DATA )[1] ).replace("zip", "csv")     
        else: clean_data_file=""       

        print('Reading data from Direccion General de Epidemiologia...')
        df, catalogo, descripcion = self.read_data()
        print('Data readed')

        if self.clean and not os.path.exists(clean_data_file): #TODO: save clean data
            print('Cleaning data')
            df = self.clean_data(df, catalogo, descripcion, preserve_original)              
            if not self.data_path is None:
                print("Save cleaned database "+clean_data_file)
                df.to_csv(clean_data_file, index=False)
        else:           
            if os.path.exists(clean_data_file) and self.clean:
                print ("Open cleaned "+clean_data_file)
                data = pd.read_csv( clean_data_file )

        print('Ready!')

        if self.return_catalogo and not self.return_descripcion:
            return df, catalogo

        if self.return_descripcion and not self.return_catalogo:
            return df, descripcion

        if self.return_catalogo and self.return_descripcion:
            return df, catalogo, descripcion


        return df

    def get_encoded_data(self, path, encoding='UTF-8'):
        try:
            data = pd.read_csv(path, encoding=encoding)
        except BaseException as e:
            if isinstance(e, UnicodeDecodeError):
                encoding = 'ISO-8859-1'
                data = self.get_encoded_data(path, encoding)
            else:
                raise RuntimeError('Cannot read the data.')

        return data

    def read_data(self, encoding='UTF-8'):
        if self.date is None:
            url_data = URL_DATA
            if not self.data_path is None:
                data_file= os.path.join( self.data_path, os.path.split( url_data )[1] )            
                if not os.path.exists(data_file):
                    wget.download(url_data, data_file)    
                    with ZipFile(data_file) as myzip:
                        myzip.infolist()
                    df_filename=myzip.infolist()[0].filename.split('.')[0]; myzip.close()
                    shutil.copyfile( data_file, data_file.replace('.zip',df_filename+'.zip') )
                
                data_path=data_file
            else:
                data_path=url_data
            
        else:
            date_f = self.date.strftime('%d.%m.%Y')
            data_path = URL_HISTORICAL.format(date_f)

        data = self.get_encoded_data(data_path)

        try:
            r_url = requests.get(URL_DESCRIPTION, stream=True)
            zip_file = ZipFile(BytesIO(r_url.content))
        except BaseException:
            raise RuntimeError('Cannot read data description.')

        catalogo = pd.read_excel(BytesIO(zip_file.read('diccionario_datos_covid19/Catalogos_0412.xlsx')), sheet_name=None, encoding='UTF-8')
        catalogo_original = {sheet: self.parse_catalogo_data(
            sheet, catalogo[sheet]) for sheet in catalogo.keys()}

        desc = pd.read_excel(BytesIO(zip_file.read('diccionario_datos_covid19/Descriptores_0419.xlsx')), encoding='UTF-8')

        return data, catalogo_original, desc

    def parse_catalogo_data(self, sheet, df):

        if 'RESULTADO' in sheet:
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
            return df

        return df

    def get_dict_replace(self, key, df):
        if key == 'ENTIDADES':
            return dict(zip(df['CLAVE_ENTIDAD'], df['ENTIDAD_FEDERATIVA']))
        elif key == 'MUNICIPIOS':
            id_mun = df['CLAVE_ENTIDAD'].astype(
                int).astype(str) + '_' + df['CLAVE_MUNICIPIO'].astype(
                int).astype(str)

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
        elif 'TEXT' in formato:
            return None
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
        if 'OTRAS_COM' in nombre_variable:
            return 'OTRA_COM'

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

    def clean_data(self, df, catalogo, descripcion, preserve_original=None):
        #Using catlogo
        catalogo_dict = {
            key.replace(
                'Catálogo ',
                '').replace(
                'de ',
                ''): df for key,
            df in catalogo.items()}
        catalogo_dict = {
            key: self.get_dict_replace(
                key,
                df) for key,
            df in catalogo_dict.items()}

        #Cleaning description
        desc_dict = dict(zip(descripcion['NOMBRE DE VARIABLE'].apply(
            self.clean_nombre_variable), descripcion['FORMATO O FUENTE'].apply(self.clean_formato_fuente)))

        df['MUNICIPIO_RES'] = df['ENTIDAD_RES'].astype(
            str) + '_' + df['MUNICIPIO_RES'].astype('Int64').astype(str)

        #Updating cols
        if preserve_original is None:
            preserve_original = []

        for col in df.columns:
            if col in preserve_original:
                new_col = col + '_original'
                df[new_col] = df[col]

            df[col] = self.replace_values(
                df, col, desc_dict, catalogo_dict)


        df.columns = df.columns.str.lower()

        return df

    def get_plot(self):
        self.return_catalogo = True
        self.return_descripcion = True
        self.clean = True

        dge_data, catalogue, description = self.get_data(preserve_original=['MUNICIPIO_RES', 'ENTIDAD_RES'])

        dge_plot = DGEPlot(dge_data, catalogue, description)
        dge_plot.date = self.date

        return dge_plot
    
