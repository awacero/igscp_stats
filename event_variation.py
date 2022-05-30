
import fnmatch
import os, sys

from matplotlib import pyplot as plt
import pandas as pd
from obspy.io.seiscomp import event 
from sqlalchemy.sql.expression import column

from bs4 import BeautifulSoup as bs

from obspy import Catalog, UTCDateTime
import zlib

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('expand_frame_repr', False)

##el evento XML esta formado por PICK, AMPLITUDE contiene el valor de magnitud, tipo de mag, 1 ORIGIN , 1 EVENTO 


def zip2catalog(file_path):
    
    zip_buffer = open(file_path, 'rb').read()
    uncompressed = zlib.decompress(zip_buffer)

    event_xml = bs(uncompressed,"xml")

    event_info = event_xml.find("event")
    modification_time = event_info.modificationTime
    
    temp_event = event._read_sc3ml(uncompressed)[0]
    temp_event.extra = { 'modification_time' : UTCDateTime(modification_time.get_text()) }
    return temp_event 

def create_zip_list(event_folder):

    file_list = []
    for dir_path, dir_names, file_names in os.walk(event_folder):
        for zip_file in file_names:
            if fnmatch.fnmatch(zip_file, '*zip'):
                file_list.append(os.path.join(dir_path,zip_file))
    return file_list


def modify_event():
    pass

"""
def get_network_magnitude(event):

    network_magnitude = []
    for m in event.magnitudes:
        network_mag_dict ={'mag':m['mag'],'type':m['magnitude_type'], 'creation_time':m.creation_info['creation_time']}
        
        network_magnitude.append(network_mag_dict)

    return network_magnitude
"""

def get_network_magnitude(event):

    """Get a list of magnitudes """

    network_magnitude = []
    ##ADD INFORMATION ABOUT EVENT VERSION TO EACH MAGNITUD
    #event.

    event_id = event.resource_id.id.split("/")[-1]

    '''Recover network magnitudes (average values of all stations)'''
    for m in event.magnitudes:
        network_mag_dict ={'mag':m['mag'],'type':m['magnitude_type'], 'creation_time':m.creation_info['creation_time'],
                            'event_id':event_id, 'modification_time':event.extra['modification_time']}
        
        network_magnitude.append(network_mag_dict)

    return network_magnitude


def add_extra_info2station_magnitude(event):

    event_id = event.resource_id.id.split("/")[-1]

    for station_mag in event.station_magnitudes:
        
        station_mag.extra =  {'modification_time':event.extra['modification_time'], 'event_id':event_id}
        print(station_mag.extra)


def create_dataframe(event_list):

    temp_list=[]

    for event in event_list:
        temp_list.append(pd.DataFrame.from_records(event.station_magnitudes ))

    return pd.concat(temp_list)


def create_simple_dataframe(event_df):

    event_df['station_id'] = event_df['waveform_id'].apply(lambda x: x.network_code + 
                                                            "_" + x.station_code + "_" + x.channel_code)
    event_df['creation_time'] = event_df['creation_info'].apply(lambda x: x.creation_time.datetime)                
    event_df['author'] = event_df['creation_info'].apply(lambda x: x.author)
    event_df['modification_time']=event_df['extra'].apply(lambda x: x['modification_time'])
    
    event_df['event_id']=event_df['extra'].apply(lambda x: x['event_id'])

    return event_df[['station_id','mag','station_magnitude_type','creation_time','author','event_id','modification_time']]
