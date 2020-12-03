'''
Created on Nov 30, 2020

@author: wacero
'''
from obspy.clients.fdsn  import Client
from obspy import UTCDateTime
from influxdb import InfluxDBClient


def get_fdsn_client(fdsn_server, fdsn_port):
    
    try:
        return Client("http://%s:%s" %(fdsn_server,fdsn_port))
    except Exception as e:
        raise Exception("Error in connect to fdsn server: %s" %str(e))

def get_events_by_day(fdsn_client,start_time,end_time):
    
    try:
        return fdsn_client.get_events(orderby="time-asc",starttime=start_time,endtime=end_time,includearrivals=True,includeallorigins=True)
        
    except Exception as e:
        raise Exception("Error in get_events_by_station_location: %s" %str(e))
    
def get_influx_client(host,port,user,passw,db_name):    
    try:
        return InfluxDBClient(host=host,port=port, username=user,password=passw,database=db_name)
    
    except Exception as e:
        raise Exception("Error creating influxdb client: %s" %str(e))  

def insert_event_2_influxdb(eventos,client_ifxdb):
    
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
            
    
    
    
    
    