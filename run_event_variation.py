

import event_variation 
import pandas as pd

events_path = "/home/wacero/borrar/iupd/"
event_file = "%s/%s" %(events_path,"igepn2022iupd.000030.xml.zip")

file_list = event_variation.create_zip_list(events_path)

event_list = []

for file_zip in file_list:
    event_list.append(event_variation.zip2catalog(file_zip))


event_single = event_list[10][0]
print(event_single)


event_network_magnitude = event_variation.get_network_magnitude(event_single)

print(event_network_magnitude)

###PROCESS USING PANDAS


station_magnitudes = pd.DataFrame.from_records(event_single.station_magnitudes)
station_magnitudes['station_id'] = station_magnitudes['waveform_id'].apply(lambda x: x.network_code + "_" + x.station_code + "_" + x.channel_code)
station_magnitudes['creation_time'] = station_magnitudes['creation_info'].apply(lambda x: x.creation_time)
#print(station_magnitudes.station_names)
#print(station_magnitudes.head())

#print(station_magnitudes['mag'],station_magnitudes['station_names'],station_magnitudes['station_magnitude_type'])

station_magnitudes_simple = station_magnitudes[['station_id','mag','station_magnitude_type','creation_time']]

print(station_magnitudes_simple.head())



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