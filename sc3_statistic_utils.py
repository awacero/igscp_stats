'''
Created on Nov 30, 2020

@author: wacero
'''
from obspy.clients.fdsn  import Client
from obspy import UTCDateTime
from influxdb import InfluxDBClient

from influxdb import DataFrameClient

def get_fdsn_client(fdsn_server, fdsn_port):
    """ 
    Cliente para conectarse a un servidor FDSN 
    
    :param string fdsn_server: IP del servidor FDSN
    :param string fdns_port: puerto FDSN
    :raises Exception e: Mensaje de excepcion
    """
    
    try:
        return Client("http://%s:%s" %(fdsn_server,fdsn_port))
    except Exception as e:
        raise Exception("Error in connect to fdsn server: %s" %str(e))

def get_events_by_day(fdsn_client,start_time,end_time):
    """ 
    Obtiene los eventos por dia 
    
    :param string fdsn_client: cliente fdsn 
    :param int start_time: hora de inicio 
    :param int end_time: hora de finalizacion 
    :return obspy.event.catalog 
    :raises Exception e: Error al obtener eventos
    """
    
    try:
        return fdsn_client.get_events(orderby="time-asc",starttime=start_time,endtime=end_time,includearrivals=True,includeallorigins=True)
        
    except Exception as e:
        raise Exception("Error in get_events_by_station_location: %s" %str(e))
    
def get_influx_client(host,port,user,passw,db_name):
    """  
    Obtiene un cliente influx
    
    :param string host: ip del servidor
    :param string port: puerto del servidor
    :param string user: usuario 
    :param string passw: contrasena
    :param string db_name: nombre de la base de datos 
    :return InfluxDBClient
    :Raises Exception e: error al crear el cliente influx
    """  
    try:
        return InfluxDBClient(host=host,port=port, username=user,password=passw,database=db_name)
    
    except Exception as e:
        raise Exception("Error creating influxdb client: %s" %str(e))  


def get_influx_DF_client(host,port,user,passw,db_name):
    """  
    Obtiene un cliente influx
    
    :param string host: ip del servidor
    :param string port: puerto del servidor
    :param string user: usuario 
    :param string passw: contrasena
    :param string db_name: nombre de la base de datos 
    :return InfluxDBClient
    :Raises Exception e: error al crear el cliente influx
    """  
    try:
        return DataFrameClient(host=host,port=port, username=user,password=passw,database=db_name)
    
    except Exception as e:
        raise Exception("Error creating influxdb DataFrame client: %s" %str(e))  



def insert_event_2_influxdb(eventos,client_ifxdb):
    """
    Guarda una lista de eventos en una base de datos de series de tiempo 
    
    :param list eventos: lista de objetos obspy.core.event
    :param string client_ifxdb: cliente influx
     
    """
    
    for i, event in enumerate(eventos):
        origin=event.preferred_origin() or event.origins[0]
        lat, lon,time=round(origin.latitude,4),round(origin.longitude,4), origin.time
            
        if event.magnitudes:
            magnitude=event.preferred_magnitude() or event.magnitudes[0]
            magnitude_value=round(magnitude.mag,4)
        else:
            magnitude_value=0
            
        if event.event_type:
            e_type=event.event_type
            event_type=e_type.replace(" ","_")
        else:
            event_type="not_set"  
        
        event_id=event['resource_id'].id[-13:]
        num_origins= len(event.origins)
        mean_picks = int(len(event.picks)/num_origins)
        
        #print(time,event_id,lat,lon, magnitude_value, num_origins, mean_picks,event_num)
        print(time, event_id, event_type)
        
        client_ifxdb.write("event_info,eventid='%s',event_type='%s' lat=%s,lon=%s,mag_value=%s,num_orig=%s,mean_pick=%s,aux_val=1  %s" 
                           %(event_id,event_type, lat,lon,magnitude_value,num_origins,mean_picks, time.ns), {'db':'sc3_events_info'},protocol='line' )
        
    
def insert_false_picks(events,client_ifxdb):
    """ 
    Guarda en una base de datos los picados de eventos falsos 
    
    :param list events: obspy.core.event 
    :param influx.client client_ifxdb: cliente ifxdb 
    """
    
    for i, event in enumerate(events):
        if event.event_type=="not existing":
            origin=event.preferred_origin() or event.origins[0]
            time=origin.time
            print("Evento falso\n")
            temp_pick_list=[]
            for i,pick in enumerate(event.picks):
                temp_pick_list.append(pick.waveform_id.station_code)
            temp_pick_set=set(temp_pick_list)
            for pick in temp_pick_set:
                print(time,pick,1)
                client_ifxdb.write("false_event_info,station_name=%s aux_val=1 %s"
                                   %(pick, time.ns),{'db':'sc3_events_info'},protocol='line')
            
            
            #print("%s\n" %event.origins)    
    
def insert_station_magnitudes(station_mag_pd, client_ifxdb):

    """
    """
    station_mag_pd.set_index('creation_time',inplace=True)
    measurement = 'magnitude_variation'
    tags = ['station_id','station_magnitude_type','author','event_id']

    try:

        client_ifxdb.write_points(dataframe=station_mag_pd, measurement=measurement,tag_columns=tags, protocol='line')

    except Exception as e:
        print("Error in insert_station_magnitudes(): %s" %e)

     
def insert_network_magnitudes(network_mag_pd, client_ifxdb):

    """
    """
    network_mag_pd.set_index('creation_time',inplace=True)
    measurement = 'network_magnitude_variation'
    tags = ['type','event_id']
    try:

        client_ifxdb.write_points(dataframe=network_mag_pd, measurement=measurement,tag_columns=tags, protocol='line')

    except Exception as e:
        print("Error in insert_station_magnitudes(): %s" %e)