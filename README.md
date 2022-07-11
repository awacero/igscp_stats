Code to create statistic information from events stored in the seiscomp3 database. 

# Create the conda environment

``` bash
$ conda create -n sc3_statistics python=3.10

$ conda activate sc3_statistics
$ conda  config --add channels conda-forge

$ conda install obspy influxdb pygelf pandas bs4

$ pip install get_mseed_data

```


# Config file options

``` bash

[RUN_MODE]
mode= SOMEDAYS | ONEDAY
data_target = STDOUT | DB 

```
