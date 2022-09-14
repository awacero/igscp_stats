 # -*- coding: utf-8 -*-

#"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from matplotlib import pyplot as plt



def get_event_from_fdsnws(fdsn_client,event_id):

    return fdsn_client.get_events(eventid=event_id,includearrivals=True,includeallorigins=True,
                        includeallmagnitudes=True, includecomments=True)
    

def generate_plotly_network_magnitud(event_network_mag_df):

    fig_scatter_n_m = px.scatter(event_network_mag_df, x="magnitude_type", y ="mag", 
        hover_data={'mag':':.2f','station_count':True,'magnitude_type':False},
        symbol="magnitude_type"    
        )

    fig_scatter_n_m.update_traces(marker=dict(size=25,color="red"))

    fig_scatter_author = px.scatter(event_network_mag_df,x="author",y="mag",
        color="mag", 
        hover_data= {'author':True,'magnitude_type':True,'mag':':.2f','mag_diff':False},
        size="mag_diff" )
        
    fig_scatter_event = px.scatter(event_network_mag_df,x="event_id",y="mag",
        color="mag",
        hover_data= {'author':True,'mag':':.2f','mag_diff':False},
        size="mag_diff"
        )

    fig_fusion = go.Figure(data = fig_scatter_n_m.data + fig_scatter_event.data + fig_scatter_author.data )
    fig_fusion.update_layout(legend=dict(orientation='h'))
    fig_fusion.show()



def generate_plotly_station_magnitud(event_network_mag_df):

    station_mag_df = pd.read_csv('./station_mag.csv')
    event_network_mag_df = pd.read_csv('./network_mag.csv')

    fig_boxplot = px.box(station_mag_df,x ="station_magnitude_type", y='mag',
        color='station_magnitude_type')
    for trace in fig_boxplot.data:
        trace['showlegend']=False

    fig_scatter_s_m = px.scatter(station_mag_df, x="station_magnitude_type",y="mag",
        color="mag", 
        hover_data= {'station_id':True,'author':True,'mag':':.2f','mag_diff':False,'station_magnitude_type':False,'time_diff':True},
        size="mag_diff" )

    fig_scatter_n_m = px.scatter(event_network_mag_df, x="magnitude_type", y ="mag", 
        hover_data={'mag':':.2f','station_count':True,'time_diff':True,'magnitude_type':False},
        symbol="magnitude_type"    
        )

    fig_scatter_n_m.update_traces(marker=dict(size=25,color="red"))

    fig_scatter_author = px.scatter(station_mag_df,x="author",y="mag",
        color="mag", 
        hover_data= {'station_id':True,'author':True,'mag':':.2f','mag_diff':False,'station_magnitude_type':False,'time_diff':True},
        size="mag_diff" )
        
    fig_scatter_event = px.scatter(station_mag_df,x="event_id",y="mag",
        color="mag",
        hover_data= {'station_id':True,'author':True,'mag':':.2f','mag_diff':False,'station_magnitude_type':False,'time_diff':True},
        size="time_diff"
        )


    fig_fusion = go.Figure(data = fig_scatter_s_m.data + fig_scatter_n_m.data + fig_boxplot.data + fig_scatter_event.data + fig_scatter_author.data )

    fig_fusion.update_layout(legend=dict(orientation='h'))

    fig_fusion.show()


#fig_boxplot.show()

#print(fig_boxplot.to_json(pretty=True))
#fig_scatter_event.show()

#print(fig_fusion)


#mueve el legend, pero se pierde al fusionar
#fig_scatter_n_m.update_layout(legend=dict(yanchor='top', y=1,x=0,xanchor='right'))

# invierte el mapa de color pero se pierde al fusionar
#,color_continuous_scale=px.colors.sequential.inferno_r
#fig_scatter_s_m.show()


#fig_scatter_s_m_author = px.scatter(station_mag_df, x="station_magnitude_type",y="mag",color="mag", hover_data= ['station_id','author'],size="mag_diff" ) 

#fig_boxplot.add_trace(fig_scatter_n_m.data[0])
#fig_boxplot.add_trace(fig_scatter_s_m.data[0])

#fig_scatter_n_m.add_trace(fig_scatter_s_m.data[0])
#fig_scatter_n_m.add_box(station_mag_df,x ="station_magnitude_type", y='mag',color='station_magnitude_type')
#fig_scatter_n_m.show()

#fig_fusion = go.Figure(data=fig_scatter_n_m.data + fig_boxplot.data)

#fig = px.scatter(event_network_mag_df, x="magnitude_type", y ="station_count", size="mag_diff",color="time_diff",hover_data=['mag','station_count','time_diff'])
#fig = px.scatter_3d(event_network_mag_df, x="magnitude_type", y ="station_count",z='modification_time', color="mag",size="mag_diff", hover_data=['mag','station_count','time_diff'] )
#fig_scatter = px.scatter_3d(event_network_mag_df, x="author", y ="mag",z='modification_time',color="mag",size="mag_diff",symbol="magnitude_type")



##NO AGREGAR EL N_M A S_M porque no se visualizan la información de N_M
##fig_scatter_s_m.add_trace(fig_scatter_n_m.data[0])
##fig_scatter_s_m.show()
##fig_scatter_s_m.show()