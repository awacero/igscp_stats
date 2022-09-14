import os, sys
import logging, logging.config
import magnitude_variation
import variation_fdsn_plotly
import event_stats

from get_mseed_data import get_mseed
from get_mseed_data import get_mseed_utils as gmutils
from obspy import UTCDateTime


if gmutils.check_file("./config/logging.ini"):
    
    logging.config.fileConfig('./config/logging.ini', disable_existing_loggers=False)
    logger=logging.getLogger('run_event_stats')



def scevtlog2influx(events_path, influx_df_client):

    event_list = [] 
    event_network_mag_list =[]
    file_list = magnitude_variation.create_zip_list(events_path)
    file_list.sort()

    for file_zip in file_list[1:]:
        try:
            event_list.append(magnitude_variation.zip2catalog(file_zip))
        except Exception as e:
            print("Error in append file: %s" %e)
            pass

    for e in event_list:
        try:
            event_network_mag_list += magnitude_variation.get_network_magnitude(e)
        except  Exception as e:
            print("Error in get_network_magnitude: %s" %e)
            pass

    for e in event_list:
        try:
            magnitude_variation.add_event_info2station_magnitude(e)
        except Exception as e:
            print("Error in add_event_info2station_magnitude: %s" %e)

            pass
    
    station_mag_df = magnitude_variation.create_station_magnitude_df(event_list)           
    event_network_mag_df = magnitude_variation.create_network_magnitude_df(event_network_mag_list)
    
    logger.info("Write data to influxdb")
    #print(station_mag_df.)
    #print(event_network_mag_df.head(10))
    #print(event_network_mag_df.mag.describe())
    event_stats.insert_station_magnitudes(station_mag_df,influx_df_client)
    event_stats.insert_network_magnitudes(event_network_mag_df ,influx_df_client)


def main():
    
    is_error = False
    
    if len(sys.argv) == 1:
        is_error = True
    
    else:
        try:
            run_param=gmutils.read_parameters(sys.argv[1])      

        except Exception as e:
            logger.error("Error reading configuration sets in file: %s" %(str(e)))
            raise Exception("Error reading configuration file: %s" %(str(e)))


        try:
            run_mode = run_param['RUN_MODE']['mode']
            data_target = run_param['RUN_MODE']['data_target'] 
            db_id=run_param['DATABASE']['id']
            db_config_file= run_param['DATABASE']['file_path']
            fdsn_id=run_param['FDSN']['id']
            fdsn_server_config_file=run_param['FDSN']['file_path']

            
        except Exception as e:
            logger.error("Error getting parameters: %s" %(e))
            raise Exception("Error getting parameters: %s" %(e))
            
            
        try:
            db_param=gmutils.read_config_file(db_config_file)
            mseed_server_param=gmutils.read_config_file(fdsn_server_config_file)
        except Exception as e:
            logger.error("Error reading configuration file: %s" %str(e))
            raise Exception("Error reading configuration file: %s" %str(e))


        try:
            logger.info("Trying to create FDSN client")
            fdsn_client = get_mseed.choose_service(mseed_server_param[fdsn_id])

        except Exception as e:
            logger.error("Failed to create fdsn client: %s" %str(e))
            raise Exception("Failed to create fdsn client: %s" %str(e))

        try:
            logger.info("Trying to create influx DF client and influx client")
            influx_df_client = event_stats.get_influx_DF_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])

            influx_client = event_stats.get_influx_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])

        except Exception as e:
            logger.error("Failed to create influx client: %s" %(e))
            raise Exception("Failed to create influx client: %s" %(e))

        #este modo se agregó para poder generar información 
        # apartir de datos desde FDSN
        if run_mode == "FDSN":
            print("start of FDSN mode. Can not recover station magnitudes")
            event_id = sys.argv[2]
            event = variation_fdsn_plotly.get_event_from_fdsnws(fdsn_client,event_id)

            event_n_m = magnitude_variation.get_network_magnitude(event[0])

            event_n_m_df = magnitude_variation.create_network_magnitude_df(event_n_m)


            print(event_n_m_df.head(10))

            variation_fdsn_plotly.generate_plotly_network_magnitud(event_n_m_df)
        
        if run_mode == "LOCAL":
            print("start of LOCAL mode. Do not send to INFLUX")
            
            events_path = sys.argv[2]
            
            event = variation_fdsn_plotly.get_event_from_fdsnws(fdsn_client,event_id)

            event_n_m = magnitude_variation.get_network_magnitude(event[0])

            event_n_m_df = magnitude_variation.create_network_magnitude_df(event_n_m)


            #print(event_n_m_df.head(10))

            variation_fdsn_plotly.generate_plotly_network_magnitud(event_n_m_df)

        elif run_mode == "SINGLE":

            events_path = sys.argv[2]

            scevtlog2influx(events_path,influx_df_client)
            
        elif run_mode == "LIST":
            
            logger.info("LIST MODE")
            events_path_file = sys.argv[2]
            events_path_list =[]
            with open(events_path_file,'r') as file:
                while (line := file.readline().rstrip()):
                    events_path_list.append(line)

            
            for events_path in events_path_list:
                logger.info("Start of event:%s" %events_path)
                scevtlog2influx(events_path, influx_df_client)
                ##CALL CREATE FUNCTION


            #print(station_mag_df.head(10))
            #print(event_network_mag_df.head(10))

    if is_error:
        logger.info(f'Usage: python {sys.argv[0]} configuration_file.txt start_date [end_date]')
        print(f'USAGE: python {sys.argv[0]} CONFIGURATION_FILE.txt start_date [end_date]') 


main()
