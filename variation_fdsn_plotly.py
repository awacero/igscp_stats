
 # -*- coding: utf-8 -*-

#"""
import event_variation 
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import sys

'''
event_list = []
event_network_mag_list =[]
#event_path = "/home/wacero/borrar/iupd/"
#event_path = "/home/wacero/borrar/igepn2022kuar/"
#event_path = "/home/wacero/borrar/igepn2022fzqp/"
event_path = "/home/wacero/borrar/igepn2022iupd/"
pd.options.display.max_colwidth =200


file_list = event_variation.create_zip_list(event_path)

for file_zip in file_list:
    try:
        event_list.append(event_variation.zip2catalog(file_zip))

    except: pass

for e in event_list:

    try:
        event_network_mag_list += event_variation.get_network_magnitude(e)
    except Exception as e: 
        print("Error in get_network_magnitude: %s" %e)
        pass


for e in event_list:
    try:
        event_variation.add_event_info2station_magnitude(e)
    except: pass


station_mag_df = event_variation.create_station_magnitude_df(event_list)

station_mag_df = event_variation.create_simple_station_mag_df(station_mag_df)

event_network_mag_df = pd.DataFrame.from_records(event_network_mag_list)



event_network_mag_df['time_diff'] =  event_network_mag_df['creation_time'] - event_network_mag_df['event_creation_time']
event_network_mag_df['time_diff'] = event_network_mag_df['time_diff'].apply( lambda x: x.total_seconds()/3600)

##COMO OBTENER VALORES POR TAMANO DE MAGNITUD
event_network_mag_df['mag_diff'] = event_network_mag_df['mag'] - event_network_mag_df['mag'].min()

event_network_mag_df['mag_diff'] = event_network_mag_df['mag_diff'].round(4)
event_network_mag_df['time_diff'] = event_network_mag_df['time_diff'].round(4)

station_mag_df['time_diff'] = station_mag_df.creation_time - station_mag_df.event_creation_time
station_mag_df['time_diff'] = station_mag_df['time_diff'].apply(lambda x: x.total_seconds()/3600)
station_mag_df['time_diff'] = station_mag_df['time_diff'].round(4)

station_mag_df['mag_diff'] = station_mag_df['mag'] - station_mag_df['mag'].min()
station_mag_df['mag_diff'] = station_mag_df['mag_diff'].round(4)

station_mag_df.set_index('creation_time',inplace=True)
event_network_mag_df.set_index('creation_time',inplace=True)


print(event_network_mag_df.head(10))
print(station_mag_df.head(10))
print("####")

#print(station_mag_df.head(10))


station_mag_df.to_csv("./station_mag.csv")
event_network_mag_df.to_csv("./network_mag.csv")

sys.exit()

'''

station_mag_df = pd.read_csv('./station_mag.csv')
event_network_mag_df = pd.read_csv('./network_mag.csv')

import plotly.express as px
import plotly.graph_objects as go



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