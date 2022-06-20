import os, sys
import logging, logging.config

from datetime import datetime
from datetime import timedelta
from get_mseed_data import get_mseed
from get_mseed_data import get_mseed_utils as gmutils

import event_variation
import pandas as pd 
from obspy import UTCDateTime
import sc3_statistic_utils as sc3_statistics

if gmutils.check_file("./config/logging.ini"):
    
    logging.config.fileConfig('./config/logging.ini', disable_existing_loggers=False)
    logger=logging.getLogger('run_sc3_statistics')




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
            influx_df_client = sc3_statistics.get_influx_DF_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])

            influx_client = sc3_statistics.get_influx_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])

        except Exception as e:
            logger.error("Failed to create influx client: %s" %(e))
            raise Exception("Failed to create influx client: %s" %(e))

        if run_mode == "SINGLE":
            
            event_list = [] 
            event_network_mag_list =[]

            events_path = sys.argv[2]

            file_list = event_variation.create_zip_list(events_path)
            file_list.sort()

            for file_zip in file_list:
                try:
                    event_list.append(event_variation.zip2catalog(file_zip))
                except:
                    pass

            for e in event_list:
                try:
                    event_network_mag_list += event_variation.get_network_magnitude(e)
                except:
                    pass

            for e in event_list:
                try:
                    event_variation.add_extra_info2station_magnitude(e)
                except:
                    pass

            event_df = event_variation.create_dataframe(event_list)

            event_simple = event_variation.create_simple_dataframe(event_df)

            #print(event_simple.head(10))
            #print(event_network_mag_list)
            event_network_mag_pd = pd.DataFrame.from_records(event_network_mag_list)



            sc3_statistics.insert_station_magnitudes(event_simple,influx_df_client)

            sc3_statistics.insert_network_magnitudes(event_network_mag_pd,influx_df_client)
            

        elif run_mode == "LIST":
            pass


    if is_error:
        logger.info(f'Usage: python {sys.argv[0]} configuration_file.txt start_date [end_date]')
        print(f'USAGE: python {sys.argv[0]} CONFIGURATION_FILE.txt start_date [end_date]') 


main()
