# -*- coding: utf-8 -*-

# """
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    fig_fusion = go.Figure(data=fig_scatter_s_m.data
                           + fig_scatter_n_m.data
                           + fig_boxplot.data
                           + fig_scatter_event.data
                           + fig_scatter_author.data)

    fig_fusion.update_layout(legend=dict(orientation='h'))

    fig_fusion.show()
