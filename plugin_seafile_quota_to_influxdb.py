#!/usr/bin/env python
# This plugin fetches quota data from the Seafile API and writes it to a local or remote InfluxDB
# Developer: Massoud Ahmed


import requests
import json
import sys
from optparse import OptionParser, OptionGroup
import logging
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS
from dateutil.tz import tzlocal
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper


LOGGER = logging.getLogger('plugin_seafile_quota_to_influxdb')
date_utils.date_helper = DateHelper(timezone=tzlocal())


def library_check(seafileAddress, seafileToken, influxdbHost, influxdbPort, influxdbToken, debug):
  tokenHeader = "Token "  + str(seafileToken)
  headers = {
                  'Authorization': tokenHeader,
                  'Accept': 'application/json; indent=4',

          }

  authURLLibrary = seafileAddress + "/api/v2.1/admin/libraries/?page=1&per_page=100"
  try:
   responseLibrary = requests.get(authURLLibrary, headers=headers)
   u = responseLibrary.text
   v = json.loads(u)
  
   # Search Seafile Repos and extract library name and size
   libraryConsumption = ""
   for library in v["repos"]:
      label = str(library["name"])
      label = str("".join(label.split())).replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("Ü","UE").replace(".","").replace("Ö","OE").replace("Ä","ae")
      libraryConsumption =int(str(library["size"]).replace(" ",""))
      # parse library name and size to influxdb
      sendData2InfluxDB(label, libraryConsumption, influxdbHost, influxdbPort, influxdbToken, debug)
      if debug:
        print("Library: " + str(label) + " Used: " +str(library["size_formatted"]))

  except:
    print("UNKNOWN: no library found. Wrong token or address!")
    raise
  return libraryConsumption


def sendData2InfluxDB(label, libraryConsumption, influxdbHost, influxdbPort, influxdbToken, debug):
  influxclient = InfluxDBClient(url=influxdbHost+":"+influxdbPort, token=influxdbToken, org="seafileMonitor", debug=debug)
  version = influxclient
  #initiate write API
  write_api = influxclient.write_api(write_options=ASYNCHRONOUS)

  # Write library quota data to bucket "seafileData"
  # Organization "seafileMonitor"
  # set measurement to "quota"
  # set key to "library"
  # set value to "libraryConsumption"

  write_api.write("seafileData", "seafileMonitor", ["quota,library="+label+' value='+str(libraryConsumption)])



def getUserQuota(seafileAddress,seafileToken,influxdbHost, influxdbPort, influxdbToken, debug):
  # get total Seafile Quota
  tokenHeader = "Token "  + str(seafileToken)
  headers = {
            'Authorization': tokenHeader,
            'Accept': 'application/json; indent=4',

    }

  authURLUser = seafileAddress + "/api/v2.1/admin/users/?page=1&per_page=100"


  responseUser = requests.get(authURLUser, headers=headers)

  x = responseUser.text

  y = json.loads(x)


  #current usage
  usage = (y["data"][0]["quota_usage"])
  #total quota
  total = (y["data"][0]["quota_total"])
  #calculate space left        
  differ = total - usage

  sendData2InfluxDB("QuotaLeft", differ, influxdbHost, influxdbPort, influxdbToken, debug)
  



  
if __name__ == "__main__":

        desc='''%prog fetches your seafile library quotas and writes them to InfluxDB'''
        parser = OptionParser(description=desc)
        gen_opts = OptionGroup(parser, "Generic options")
        host_opts = OptionGroup(parser, "Host options")
        influxdb_opts = OptionGroup(parser, "InfluxDB options")
        

        parser.add_option_group(gen_opts)
        parser.add_option_group(host_opts)
        parser.add_option_group(influxdb_opts)

        #-d / --debug
        gen_opts.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")
        

        #-U / --url
        host_opts.add_option("-u", "--url", dest="url", default=None, action="store", metavar="URL", help="Seafile server address")

        #-s / --seafiletoken
        host_opts.add_option("-s", "--seafiletoken", dest="seafiletoken", default=None, action="store", metavar="TOKEN", help="Seafile server token")

      	#-H / --host                                                                                                                                                                                                                                      
        influxdb_opts.add_option("-H", "--host", dest="host", default="http://127.0.0.1", action="store", metavar="HOST", help="InfluxDB Host (default: http://localhost)")

        #-p / --port
        influxdb_opts.add_option("-p", "--port", dest="port", default="8086", action="store", metavar="PORT", help="InfluxDB Host (default: 8086)")


        #-t / --token
        influxdb_opts.add_option("-t", "--token", dest="influxdbtoken", default=None, action="store", metavar="PORT", help="InfluxDB Token (mandatory)")






        #parse arguments
        (options, args) = parser.parse_args()


        seafileAddress = options.url
        seafileToken = options.seafiletoken
        influxdbHost = options.host
        influxdbPort = options.port
        influxdbToken = options.influxdbtoken

        



  
        
        #set loggin
        if options.debug:
          logging.basicConfig(level=logging.DEBUG)
          LOGGER.setLevel(logging.DEBUG)
        else:
          logging.basicConfig()
          LOGGER.setLevel(logging.INFO)
       
        library_check(seafileAddress, seafileToken, influxdbHost, influxdbPort, influxdbToken, options.debug)
        getUserQuota(seafileAddress,seafileToken,influxdbHost, influxdbPort, influxdbToken, options.debug)

