
import fnmatch
import os, sys
from types import NoneType

from matplotlib import pyplot as plt
import pandas as pd
from obspy.io.seiscomp import event 
from sqlalchemy.sql.expression import column

from bs4 import BeautifulSoup as bs

from obspy import Catalog, UTCDateTime
import zlib

import numpy as np

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('expand_frame_repr', False)

##el evento XML esta formado por PICK, AMPLITUDE contiene el valor de magnitud,
#  tipo de mag, 1 ORIGIN , 1 EVENTO 

def create_zip_list(event_folder):

    '''
    Create a  list of paths for each xml.zip file
    '''
    file_list = []
    for dir_path, dir_names, file_names in os.walk(event_folder):
        for zip_file in file_names:
            if fnmatch.fnmatch(zip_file, '*zip'):
                file_list.append(os.path.join(dir_path,zip_file))
    return file_list

def zip2catalog(file_path):
    '''
    Uncompress the zip file, convert the xml to a obspy.core.event object
    '''
    zip_buffer = open(file_path, 'rb').read()
    uncompressed = zlib.decompress(zip_buffer)
    #event_xml = bs(uncompressed,"xml")
    #event_info = event_xml.find("event")
    #modification_time = event_info.modificationTime
    temp_event = event._read_sc3ml(uncompressed)[0]
    temp_event.extra = { 'modification_time' : add_modification_time(uncompressed) }
    
    return temp_event 


def add_modification_time(event_xml_uncompressed):

    try:
        event_xml = bs(event_xml_uncompressed, "xml")
        event_info = event_xml.find("event")
        modification_time = UTCDateTime(event_info.modificationTime.get_text())
        return modification_time

    except:
        return ""
    


def get_network_magnitude(event):

    """
    Get the list of network magnitudes of an event
    """

    network_magnitude = []
    event_id = event.resource_id.id.split("/")[-1]
    event_creation_time = event.creation_info['creation_time'].datetime
    
    for m in event.magnitudes:
        network_mag_dict ={
            #'mag':round(m['mag'],4),
            'magnitude_type':m['magnitude_type'], 
            'creation_time':m.creation_info['creation_time'].datetime,
            'author':m.creation_info['author'],
            'station_count':m['station_count'], 
            #'mag_uncertainty':round(m.mag_errors['uncertainty'],4) or 0,
            #'evaluation_mode':m['evaluation_mode'], 'evaluation_status':m['evaluation_status'],
            'event_id':event_id, 'modification_time':event.extra['modification_time'].datetime,  
            'event_creation_time':event_creation_time  }
        
        if m.mag_errors['uncertainty'] is not NoneType and m.mag_errors['uncertainty'] is not None:
            network_mag_dict['mag_uncertainty'] = round(m.mag_errors['uncertainty'],4)
        else:
            network_mag_dict['mag_uncertainty'] = np.nan

        if m['mag'] is not NoneType and m['mag'] is not None:
            network_mag_dict['mag'] = round(m['mag'],4)

        else:
            network_mag_dict['mag']= np.nan                    

        network_magnitude.append(network_mag_dict)

    return network_magnitude


def add_event_info2station_magnitude(event):

    event_id = event.resource_id.id.split("/")[-1]
    event_creation_time = event.creation_info['creation_time'].datetime
    for station_mag in event.station_magnitudes:        
        station_mag.extra =  {'modification_time':event.extra['modification_time'].datetime, 
            'event_id':event_id, 'event_creation_time':event_creation_time}


def add_amplitud2station_magnitude(event):


    pass


def create_station_magnitude_df(event_list):

    temp_list=[]

    for event in event_list:
        temp_list.append(pd.DataFrame.from_records(event.station_magnitudes ))

    return pd.concat(temp_list)

def create_amplitude_df(event_list):

    temp_list=[]

    for event in event_list:
        temp_list.append(pd.DataFrame.from_records(event.amplitudes ))

    return pd.concat(temp_list)

def create_simple_station_mag_df(station_mag_df):

    station_mag_df['station_id'] = station_mag_df['waveform_id'].apply(lambda x: x.network_code + 
                                                            "_" + x.station_code + "_" + x.channel_code)
    station_mag_df['creation_time'] = station_mag_df['creation_info'].apply(lambda x: x.creation_time.datetime)                
    station_mag_df['author'] = station_mag_df['creation_info'].apply(lambda x: x.author)
    station_mag_df['modification_time']=station_mag_df['extra'].apply(lambda x: x['modification_time'])
    
    station_mag_df['event_creation_time'] = station_mag_df['extra'].apply(lambda x: x['event_creation_time'])

    station_mag_df['event_id']=station_mag_df['extra'].apply(lambda x: x['event_id'])

    station_mag_df['amplitude_id'] = station_mag_df['amplitude_id'].apply(lambda x: x.id)
    station_mag_df['mag'] = station_mag_df.mag.round(4)

    return station_mag_df[['creation_time','station_id','mag','station_magnitude_type','author',
    'event_id','modification_time','event_creation_time','amplitude_id']]

