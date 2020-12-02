
import sc3_statistic_utils as utils
from obspy.core import UTCDateTime

fdsn_server="192.168.1.35"
fdsn_port= '8080'

ifx_host='192.168.1.90'
ifx_port=8086
ifx_user='sc3statistic'
ifx_pass='estadisticaClave'
ifx_dbname='sc3_events_info'

fdsn_cl=utils.get_fdsn_client(fdsn_server, fdsn_port) 
influx_client=utils.get_influx_client(ifx_host,ifx_port,ifx_user,ifx_pass,ifx_dbname)

end_time=UTCDateTime.now()

start_time=end_time-86400

eventos= utils.get_events_by_day(fdsn_cl, start_time, end_time)

utils.insert_event_2_influxdb(eventos, influx_client)