
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
    

def fdsn_network_magnitude(event):

    event_id = event.resource_id.id.split("/")[-1]
    event_creation_time = event.creation_info['creation_time'].datetime

    network_magnitude = []

    for m in event.magnitudes:

        network_mag_dict = { 
            'magnitude_type':m['magnitude_type'], 
            'creation_time':m.creation_info['creation_time'].datetime,
            'author':m.creation_info['author'],
            'station_count':m['station_count'], 
            'event_id':event_id,  
            'event_creation_time':event_creation_time 
                }
        if m.mag_errors['uncertainty'] is not NoneType and m.mag_errors['uncertainty'] is not None:
            network_mag_dict['mag_uncertainty'] = round(m.mag_errors['uncertainty'],4)
        else:
            network_mag_dict['mag_uncertainty'] = np.nan

        if m['mag'] is not NoneType and m['mag'] is not None:
            network_mag_dict['mag'] = round(m['mag'],4)

        else:
            network_mag_dict['mag']= np.nan                    

        network_magnitude.append(network_mag_dict)

    pass 


def get_network_magnitude(event):

    """
    Get the list of network magnitudes of an event
    """

    network_magnitude = []
    event_id = event.resource_id.id.split("/")[-1]
    #print( "##CTM %s" %event.creation_info['creation_time'])
    event_creation_time = event.creation_info['creation_time'].datetime

    
    for m in event.magnitudes:
        network_mag_dict ={
            'magnitude_type':m['magnitude_type'], 
            'creation_time':m.creation_info['creation_time'].datetime,
            'author':m.creation_info['author'],
            'station_count':m['station_count'], 
            'event_id':event_id, 
             
            'event_creation_time':event_creation_time  }
        
        if m.mag_errors['uncertainty'] is not NoneType and m.mag_errors['uncertainty'] is not None:
            network_mag_dict['mag_uncertainty'] = round(m.mag_errors['uncertainty'],4)
        else:
            network_mag_dict['mag_uncertainty'] = np.nan

        if m['mag'] is not NoneType and m['mag'] is not None:
            network_mag_dict['mag'] = round(m['mag'],4)

        else:
            network_mag_dict['mag']= np.nan                    

        if hasattr(event, 'extra'):
            network_mag_dict['modification_time'] = event.extra['modification_time'].datetime
        else:
            network_mag_dict['modification_time'] = event_creation_time


        network_magnitude.append(network_mag_dict)

    return network_magnitude


def add_event_info2station_magnitude(event):

    event_id = event.resource_id.id.split("/")[-1]
    event_creation_time = event.creation_info['creation_time'].datetime
    for station_mag in event.station_magnitudes:        
        station_mag.extra =  {'event_id':event_id, 'event_creation_time':event_creation_time}


        if hasattr(event,'extra'):
            station_mag.extra['modification_time'] = event.extra['modification_time'].datetime
        else:
            station_mag.extra['modification_time'] = event_creation_time



def add_amplitud2station_magnitude(event):


    pass


def create_station_magnitude_df(event_list):

    temp_list=[]

    for event in event_list:
        temp_list.append(pd.DataFrame.from_records(event.station_magnitudes ))

    st_mag_df = pd.concat(temp_list)
    

    st_mag_df['station_id'] = st_mag_df['waveform_id'].apply(lambda x: x.network_code + 
                                                            "_" + x.station_code + "_" + x.channel_code)
    st_mag_df['creation_time'] = st_mag_df['creation_info'].apply(lambda x: x.creation_time.datetime)                
    st_mag_df['author'] = st_mag_df['creation_info'].apply(lambda x: x.author)
    
    st_mag_df['modification_time']=st_mag_df['extra'].apply(lambda x: x['modification_time'] if x['modification_time'] else np.nan)
    st_mag_df['event_creation_time'] = st_mag_df['extra'].apply(lambda x: x['event_creation_time'] if x else np.nan)
    st_mag_df['event_id']=st_mag_df['extra'].apply(lambda x: x['event_id'] if x else np.nan)
    st_mag_df['amplitude_id'] = st_mag_df['amplitude_id'].apply(lambda x: x.id)
    st_mag_df['mag'] = st_mag_df.mag.round(4)

    station_mag_df = st_mag_df[['creation_time','station_id','mag','station_magnitude_type',
            'author', 'event_id','modification_time','event_creation_time','amplitude_id']].copy()

    #station_mag_df['time_diff'] = station_mag_df.creation_time - station_mag_df.event_creation_time
    #station_mag_df['time_diff'] = station_mag_df['time_diff'].apply(lambda x: x.total_seconds()/3600)
    #station_mag_df['time_diff'] = station_mag_df['time_diff'].round(4)
    station_mag_df['modification_time'] = station_mag_df['modification_time'].apply(lambda x: x.isoformat())
    station_mag_df['event_creation_time'] = station_mag_df['event_creation_time'].apply(lambda x: x.isoformat())
    station_mag_df['mag_diff'] = station_mag_df['mag'] - station_mag_df['mag'].mean()
    station_mag_df['mag_diff'] = station_mag_df['mag_diff'].round(4).abs()
    
    print((st_mag_df.modification_time,st_mag_df.creation_time))
    print(st_mag_df.modification_time - st_mag_df.creation_time)
    station_mag_df.dropna(inplace=True)
    station_mag_df.set_index('creation_time',inplace=True)

    return station_mag_df


def create_network_magnitude_df(event_network_mag_list):
    event_network_mag_df = pd.DataFrame.from_records(event_network_mag_list)

    event_network_mag_df.dropna(inplace=True)
    
    #event_network_mag_df['time_diff'] =  event_network_mag_df['creation_time'] - event_network_mag_df['event_creation_time']
    #event_network_mag_df['time_diff'] = event_network_mag_df['time_diff'].apply( lambda x: x.total_seconds()/3600)
    #event_network_mag_df['time_diff'] = event_network_mag_df['time_diff'].round(4)
    
    event_network_mag_df.modification_time = event_network_mag_df.modification_time.apply(lambda x: x.isoformat())
    event_network_mag_df.event_creation_time = event_network_mag_df.event_creation_time.apply(lambda x: x.isoformat())
    ##COMO OBTENER VALORES POR TAMANO DE MAGNITUD
    event_network_mag_df['mag_diff'] = event_network_mag_df['mag'] - event_network_mag_df['mag'].mean()
    event_network_mag_df['mag_diff'] = event_network_mag_df['mag_diff'].round(4).abs()

    event_network_mag_df.set_index('creation_time',inplace=True)
    
    return event_network_mag_df 


def create_amplitude_df(event_list):

    temp_list=[]

    for event in event_list:
        temp_list.append(pd.DataFrame.from_records(event.amplitudes ))

    return pd.concat(temp_list)





