
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

##el evento XML esta formado por PICK, AMPLITUDE contiene el valor de magnitud, tipo de mag, 1 ORIGIN , 1 EVENTO 


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

def get_network_magnitude(event):

    network_magnitude = []
    for m in event.magnitudes:
        network_mag_dict ={'mag':m['mag'],'type':m['magnitude_type'], 'creation_time':m.creation_info['creation_time']}
        network_magnitude.append(network_mag_dict)

    return network_magnitude

    