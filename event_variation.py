
import fnmatch
import os, sys

from matplotlib import pyplot as plt
import pandas as pd
from obspy.io.seiscomp import event 
from sqlalchemy.sql.expression import column

import zlib

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('expand_frame_repr', False)


def zip2catalog(file_path):
    
    zip_buffer = open(file_path, 'rb').read()
    uncompressed = zlib.decompress(zip_buffer)
    return event._read_sc3ml(uncompressed)
    

def create_zip_list(event_folder):

    file_list = []
    for dir_path, dir_names, file_names in os.walk(event_folder):
        for zip_file in file_names:
            if fnmatch.fnmatch(zip_file, '*zip'):
                file_list.append(os.path.join(dir_path,zip_file))
    return file_list


events_path = "/home/wacero/borrar/iupd/"
event_file = "%s/%s" %(events_path,"igepn2022iupd.000030.xml.zip")



file_list = create_zip_list(events_path)

event_list = []

for file_zip in file_list:
    event_list.append(zip2catalog(file_zip))

print(event_list)
station_magnitudes = pd.DataFrame.from_records(event_list[10][0].station_magnitudes)

print(station_magnitudes)



"""
event_igepn = event._read_sc3ml(event_file)
print(event_igepn)

for ev in event_igepn:
    
    print(ev.magnitudes)
    for mag in ev.magnitudes:
        print("###")
        #print(type(mag))
        print(mag.resource_id())
    print(ev.origins)
    for info in ev.origins:
        print("--")
        print(info)
        
        
    for station_mag in ev.station_magnitudes:
        print(station_mag)
"""


'''

station_magnitudes = pd.DataFrame.from_records(event_igepn[0].station_magnitudes)

#print(station_magnitudes)

#for wave in station_magnitudes['waveform_id']:
#    print(wave.station_code)

station_magnitudes['station_names'] = station_magnitudes['waveform_id'].apply(lambda x: x.station_code)

station_magnitudes['station_names_mag'] = station_magnitudes['station_names'] + station_magnitudes['station_magnitude_type'] 
station_magnitudes['station_names_mag'].str.replace(' ','')
#station_magnitudes['station_names_mag'].str.replace('\n','')
print("CTM")
print ( station_magnitudes['station_names_mag'][:10] )

station_magnitudes_df = station_magnitudes.reindex(['station_names_mag','mag'])
#print(station_magnitudes)

#station_magnitudes.plot(x= station_magnitudes['station_names_mag'], y=station_magnitudes['mag'])



#test= pd.DataFrame([1,2,3], index=['A','B','C'],columns=['num1, num2, num3'])

data =[station_magnitudes['mag'],station_magnitudes['station_names_mag']]

headers = ['mag','station_names_mag']


test = pd.concat(data,axis=1, keys=headers)
#test = pd.DataFrame(station_magnitudes.station_names_mag)

print(test.head())

plt.scatter(test.station_names_mag,test.mag)
plt.xticks(test.station_names_mag,rotation='vertical')

plt.show()
#print(event)

''' 