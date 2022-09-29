# -*- coding: utf-8 -*-

# """
from enum import auto
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from matplotlib import pyplot as plt


def get_event_from_fdsnws(fdsn_client, event_id):

    """
    It gets an event from FDSN Web Services using an event_id
    and a FDSN client..

    :param fdsn_client: fdsn client object
    :param event_id: event identifier
    :returns: fdsn_client object
    """

    return fdsn_client.get_events(eventid=event_id,
                                  includearrivals=True,
                                  includeallorigins=True,
                                  includeallmagnitudes=True,
                                  includecomments=True)


def generate_plotly_magnitude_variation(network_mag_df, station_mag_df):

    """
    Takes two dataframes: ``network_mag_df`` and ``station_mag_df``;
    and then graph these dataframes using plotly library.

    :param network_mag_df: network magnitud dataframe
    :param station_mag_df: station magnitud dataframe
    :returns: plot
    """
    

    fig_boxplot = px.box(station_mag_df,
                         x="station_magnitude_type", y='mag',
                         color='station_magnitude_type')
    for trace in fig_boxplot.data:
        trace['showlegend'] = False

    fig_scatter_s_m = \
        px.scatter(station_mag_df, x="station_magnitude_type", y="mag",
                   color="mag",
                   hover_data={'station_id': True, 'author': True,
                               'mag': ':.2f', 'mag_diff': False,
                               'station_magnitude_type': False
                               },
                   size="mag_diff")

    fig_scatter_n_m = \
        px.scatter(network_mag_df, x="magnitude_type", y="mag",
                   hover_data={'mag': ':.2f', 'station_count': True,
                               'magnitude_type': False
                               },
                   symbol="magnitude_type",
                   size=network_mag_df.mag_diff.div(100)
                   )

    fig_scatter_n_m.update_traces(marker=dict(size=25, color="red"))

    fig_scatter_author = px.scatter(
        station_mag_df, x="author", y="mag",
        color="mag",
        hover_data={'station_id': True, 'author': True,
                    'mag': ':.2f', 'mag_diff': False,
                    'station_magnitude_type': False
                    },
        size="mag_diff")

    fig_scatter_event = px.scatter(
        station_mag_df, x="event_id", y="mag",
        color="mag",
        hover_data={
            'station_id': True, 'author': True, 'mag': ':.2f',
            'mag_diff': False, 'station_magnitude_type': False},
        size="mag_diff")

    fig_3d_author = px.scatter_3d(
        data_frame = station_mag_df, x="author", y="modification_time", z="mag",
        color="mag",
        symbol='station_magnitude_type', opacity=0.5,
        hover_data={
            'station_id': True, 'author': True, 'mag': ':.2f',
            'mag_diff': False, 'station_magnitude_type': False,
            'modification_time': True}
    )

    plot_rows=2
    plot_cols=1

    fig_fusion = make_subplots(rows=plot_rows, cols=plot_cols, shared_yaxes=False,
                               shared_xaxes=False, vertical_spacing=0.09,
                               row_width=[0.5, 0.5],
                               specs=[[{"type": "xy"}],
                                      [{"type": "scene"}]],
                               subplot_titles=("Magnitude Variation Graph",
                                               "Author-Modification time-Magnitude Graph"))

    data = fig_scatter_s_m.data + fig_scatter_n_m.data + fig_boxplot.data + fig_scatter_event.data + fig_scatter_author.data
    data_3d = fig_3d_author.data

    fig_fusion.add_traces(data,rows=1, cols=1)
    fig_fusion.update_layout(legend=dict(orientation='h'),height=1500, width=1300)

    fig_fusion.add_traces(data_3d,rows=2, cols=1)
    fig_fusion.update_layout(scene = dict(
                    xaxis_title='Author',
                    yaxis_title='Modification time',
                    zaxis_title='Magnitude',
                    xaxis = dict(
                         backgroundcolor="rgb(200, 200, 230)",
                         gridcolor="white",
                         showbackground=True,
                         zerolinecolor="white",),
                    yaxis = dict(
                        backgroundcolor="rgb(230, 200,230)",
                        gridcolor="white",
                        showbackground=True,
                        zerolinecolor="white"),
                    zaxis = dict(
                        backgroundcolor="rgb(230, 230,200)",
                        gridcolor="white",
                        showbackground=True,
                        zerolinecolor="white",),),
                    margin=dict(r=20, b=20, l=20, t=20))
    
    fig_fusion.show()
