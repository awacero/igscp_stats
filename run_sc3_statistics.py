
import os, sys
import logging, logging.config

from datetime import datetime
from datetime import timedelta
from get_mseed_data import get_mseed
from get_mseed_data import get_mseed_utils as gmutils


from obspy import UTCDateTime
import sc3_statistic_utils as sc3_statistics

if gmutils.check_file("./config/logging.ini"):
    
    logging.config.fileConfig('./config/logging.ini', disable_existing_loggers=False)
    logger=logging.getLogger('run_sc3_statistics')

##USAR MAGNITUDE_TYPE en lugar de TYPE 


def main():
    """
    Insert events information in a timeseries database that will be plotted using grafana or plotly 
    Do the following tasks
    Check input arguments are suplied

    """


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
            logger.info("Trying to create influx client")
            influx_client = sc3_statistics.get_influx_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])
            
            influx_df_client = sc3_statistics.get_influx_DF_client(db_param[db_id]['host'],db_param[db_id]['port'],
                                                             db_param[db_id]['user'],db_param[db_id]['pass'],
                                                             db_param[db_id]['DB_name'])
        except Exception as e:
            logger.error("Failed to create influx client: %s" %(e))
            raise Exception("Failed to create influx client: %s" %(e))

        ##AGREGAR FUNCION PARA IMPRIMIR RESULTADO EN PANTALLA
        if run_mode == "SINGLE":

            event_id = sys.argv[2]
            event = sc3_statistics.get_event_by_id(fdsn_client,event_id)
            print(event[0].preferred_origin().creation_info.creation_time.datetime)

        elif run_mode == "ONEDAY":

            if len(sys.argv) == 3:
                logger.info("Running in ONEDAY mode")
                try:
                    start_time= UTCDateTime(datetime.strptime(sys.argv[2],"%Y-%m-%d"))
                    end_time = UTCDateTime(start_time + 86400).strftime("%Y-%m-%d 00:00")
                    
                    logger.info("Get events for: %s %s" %(start_time,end_time) )
                    eventos= sc3_statistics.get_events_by_day(fdsn_client, start_time, end_time)
                    event_df = sc3_statistics.event2dataframe(eventos)
                    #event_df.to_csv('./eventos.csv')
                    sc3_statistics.insert_events_df(event_df,influx_df_client)
                    sc3_statistics.insert_false_picks(eventos,influx_client)
                
                except Exception as e:
                    raise Exception("Error getting days : %s" %str(e))
            else:
                print(f'USAGE: python {sys.argv[0]} CONFIGURATION_FILE.txt JUST NEED start_date')
                logger.error("Error in run_mode configured: %s. JUST NEED start_date " %run_mode)
                raise Exception("Error in run_mode configured: %s. JUST NEED start_date" %run_mode) 
        
        elif run_mode == "SOMEDAYS":
            
            if len(sys.argv) == 4:
                logger.info("Running in SOMEDAYS mode")
                try:
                    start_date = UTCDateTime(datetime.strptime(sys.argv[2],"%Y-%m-%d"))
                    end_date = UTCDateTime(datetime.strptime(sys.argv[3],"%Y-%m-%d"))
                    delta = end_date.datetime - start_date.datetime
                    
                    for i in range(delta.days):
                        temp_start = UTCDateTime(start_date + timedelta(days=i))
                        temp_end = temp_start + 86400
                        eventos= sc3_statistics.get_events_by_day(fdsn_client, temp_start, temp_end)

                        event_df = sc3_statistics.event2dataframe(eventos)
                        sc3_statistics.insert_events_df(event_df,influx_df_client)
                        sc3_statistics.insert_false_picks(eventos, influx_client)
                        #sc3_statistics.insert_event_2_influxdb(eventos, influx_client)


                except Exception as e:
                    raise Exception("Error getting days : %s" %str(e))

            else:
                logger.info(f'Usage: python {sys.argv[0]} configuration_file.txt start_date [end_date]')
                print(f'USAGE: python {sys.argv[0]} CONFIGURATION_FILE.txt start_date [end_date]')                 

    if is_error:
        logger.info(f'Usage: python {sys.argv[0]} configuration_file.txt start_date [end_date]')
        print(f'USAGE: python {sys.argv[0]} CONFIGURATION_FILE.txt start_date [end_date]') 


main()

