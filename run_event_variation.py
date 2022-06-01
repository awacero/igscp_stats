 # -*- coding: utf-8 -*-

import event_variation 
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import sys


event_list = []
event_network_mag_list =[]
events_path = "/home/wacero/borrar/igepn2022fzqp/"


"""
Contar el numero de picks de cada version?
Contar el numero de magnitudes de cada version
Tomar en cuenta el autor y fecha de creacion de pick y amplitud 
amplitude: usar? timeWindow? begin, end? SNR? 
información de ORIGINS: número de orígines por evento, variacion de tiempo origen, lat, lon, depth 
"""

'''
Read the event's folder 
Read the zip files without decompressing
Read the network magnitudes 
Transform all data in a dataframe
'''


file_list = event_variation.create_zip_list(events_path)

for file_zip in file_list:
    try:
        event_list.append(event_variation.zip2catalog(file_zip))

    except: pass

for e in event_list:

    try:
        event_network_mag_list += event_variation.get_network_magnitude(e)
    except: pass

for e in event_list:
    try:
        event_variation.add_extra_info2station_magnitude(e)
    except: pass


event_df = event_variation.create_dataframe(event_list)

event_simple = event_variation.create_simple_dataframe(event_df)

#print(event_simple.head(10))

event_network_mag_pd = pd.DataFrame.from_records(event_network_mag_list)

event_simple.set_index('creation_time',inplace=True)
event_network_mag_pd.set_index('creation_time',inplace=True)
print(event_network_mag_pd)
print("####")
print(event_simple.head(10))


#for e in event_network_mag_list:
#    print(e)
    #print(event_network_mag_list[0:10])


''' 
s_m_s = event_simple.copy()


for event_net_mag in event_network_mag_list:
    if event_net_mag['type'] == 'M':
        print(event_net_mag)
        plt.axhline(y=event_net_mag['mag'], linestyle='dotted',color='r')

plt.show()

ax = sns.boxplot(y='mag', x='station_magnitude_type',data=s_m_s,palette='colorblind',hue='station_magnitude_type')
sns.stripplot(y='mag', x='station_magnitude_type',data=s_m_s,jitter=True,dodge=True, marker='o', alpha=0.5,hue='station_magnitude_type')
ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)
ax.legend(bbox_to_anchor=(1,1.0), loc = 'upper left')
plt.show()
''' 



