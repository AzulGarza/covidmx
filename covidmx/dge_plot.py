from mapsmx import MapsMX
import pandas as pd
import matplotlib.pyplot as plt

class DGEPlot:
    """
    Class to plot dge information
    """

    def __init__(self, dge_data, catalogue, description):

        self.dge_data = self.prepare_data(dge_data)
        self.dge_data['cve_ent'] = self.dge_data['cve_ent'].astype(int).astype(str)
        self.catalogue = catalogue
        self.description = description

        #Downloading geo information
        state_geo = MapsMX().get_geo('state')
        state_geo['cve_ent'] = state_geo['cve_ent'].astype(int).astype(str)

        mun_geo = MapsMX().get_geo('municipality')
        mun_geo[['cve_ent', 'cve_mun']] = mun_geo[['cve_ent', 'cve_mun']].astype(int).astype(str)
        mun_geo['cve_mun'] = mun_geo['cve_ent'] + '_' + mun_geo['cve_mun']


        self.state_geo = state_geo
        self.mun_geo = mun_geo
        self.available_states = self.dge_data['entidad_res'].unique()
        self.available_status = ['confirmados', 'negativos', 'sospechosos', 'muertos']

    def prepare_data(self, df):

        df = df.rename(columns={
                       'entidad_res_original': 'cve_ent',
                       'municipio_res_original': 'cve_mun'
                       })

        df['muertos'] = df['fecha_def'].notna().astype(int)

        replace_resultado = {'Positivo SARS-CoV-2': 'confirmados',
                             'No positivo SARS-CoV-2': 'negativos',
                             'Resultado pendiente':'sospechosos'}

        df['resultado'] = df['resultado'].replace(replace_resultado)
        df = pd.concat([df, pd.get_dummies(df['resultado'])], axis=1)

        int_vars = list(replace_resultado.values()) + ['muertos']
        df[int_vars] = df[int_vars].astype(int)

        return df

    def plot_map(self, status='confirmados', state=None,
                 add_municipalities=False, save_file_name = None,
                 cmap='Reds',
                 scheme='quantiles', k=4, legend=True, zorder=1,
                 missing_kwds={'color': 'lightgray', 'label': 'Sin info'}, **kwargs):
        """
        Plot geography information

        Parameters
        ----------
        status: str
            One of confirmados, sospechosos, negativos, muertos
        state: str
            Plot particular state.
        add_municipalities: bool
            Wheter add municipalities to plot
        """

        assert status in self.available_status, 'Please provide some of the following status: {}'.format(', '.join(self.available_status))
        if state is not None:
            assert state in self.available_states, 'Please provide some of the following states: {}'.format(', '.join(self.available_states))

        # if last_date_to_consider is not None:
        #     last_date = pd.to_datetime(last_date_to_consider, format=format_date)
        #     plot_data = self.dge_data[self.dge_data['fecha_sintomas']<=last_date]
        # else:
        #     plot_data = self.dge_data

        group_cols = ['entidad_res', 'cve_ent']

        if add_municipalities:
            group_cols += ['municipio_res', 'cve_mun']

        needed_cols = [status] + group_cols

        plot_data = self.dge_data[needed_cols]
        state_geo_plot = self.state_geo
        mun_geo_plot = self.mun_geo

        if state is not None:
            plot_data = plot_data[plot_data['entidad_res'].str.lower() == state.lower()]
            cve_ent = str(plot_data['cve_ent'].unique()[0])
            state_geo_plot = self.state_geo[self.state_geo['cve_ent']==cve_ent]
            mun_geo_plot = self.mun_geo[self.mun_geo['cve_ent']==cve_ent]

        plot_data = plot_data.groupby(group_cols).agg(sum).reset_index()

        if add_municipalities:
            plot_data = plot_data.drop(columns='cve_ent')
            plot_data = mun_geo_plot.merge(plot_data, how='left', on='cve_mun')

            geometry = 'geometry_mun'
        else:
            plot_data = state_geo_plot.merge(plot_data, how='left', on='cve_ent')
            geometry = 'geometry_ent'

        base = state_geo_plot.boundary.plot(color=None,
                                            edgecolor='black',
                                            linewidth=0.6,
                                            figsize=(10,9))

        if add_municipalities and state is not None:
            mun_geo_plot.boundary.plot(ax=base, color=None,
                                       edgecolor='black',
                                       linewidth=0.2)

        plot_obj = plot_data.set_geometry(geometry).plot(ax=base,
                                                         column=status,
                                                         cmap=cmap,
                                                         scheme=scheme,
                                                         k=k,
                                                         legend=legend,
                                                         zorder=zorder,
                                                         missing_kwds=missing_kwds,
                                                         **kwargs)
        base.set_axis_off()
        plt.axis('equal')

        title = 'Casos ' + status + ' por COVID-19'

        if state is not None:
            title += '\n'
            title += state.title()

        act_date = self.date
        if self.date is None:
            act_date = self.dge_data['fecha_actualizacion'][0]
        act_date = act_date.date()
        act_date = str(act_date)

        title += '\n'
        title += 'Fecha de actualizacion de los datos: {}'.format(act_date)


        plt.title(title, fontsize=20)


        if save_file_name is not None:
            plt.savefig(save_file_name, bbox_inches='tight', pad_inches=0)
            plt.close()
        else:
            plt.show()


        return plot_obj
