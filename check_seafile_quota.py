#!/usr/bin/env python
#This script checks the remaining seafile space via API. An API token is required.
# curl -d "username=username@example.com&password=123456" https://yourseafilecloudadress/api2/auth-token/
# {"token": "24fd3c026886e3121b2ca630805ed425c272cb96"}
#For further information visit https://seafile.gitbook.io/seafile-server-manual/developing/web-api-v2.1
#Developer: Massoud Ahmed


import sys, psutil, getopt
import requests
import json
from ast import literal_eval

#nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2
usage = 'usage: ./check_seafile-quota -w/--warn <integer> -c/--crit <integer> -t/--token <token> -a/--adress <adress>'

#get quota via API
def used_quota(tok, url):
  tokenHeader = "Token "  + str(tok)
  headers = {
            'Authorization': tokenHeader,
            'Accept': 'application/json; indent=4',
    
    }

  authURLUser = url + "/api/v2.1/admin/users/?page=1&per_page=100" 

  

  responseUser = requests.get(authURLUser, headers=headers)

  x = responseUser.text

  y = json.loads(x)


  #current usage
  usage = (y["data"][0]["quota_usage"])
  #total quota
  total = (y["data"][0]["quota_total"])
  #space left
  differ = total - usage
  percent = (round(float(100-(int(usage)/int(total))*100),2))

  
  return differ, percent

def library_check(tok, url):
  tokenHeader = "Token "  + str(tok)
  headers = {
                  'Authorization': tokenHeader,
                  'Accept': 'application/json; indent=4',

          }

  authURLLibrary = url + "/api/v2.1/admin/libraries/?page=1&per_page=100"
  try:
   responseLibrary = requests.get(authURLLibrary, headers=headers)
   u = responseLibrary.text
   v = json.loads(u)
  
   libraryConsumption = ""
   for library in v["repos"]:
    if (library["name"]) != "Meine Bibliothek":
      label = str(library["name"])
      label = str("".join(label.split())).replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("Ü","UE").replace(".","").replace("Ö","OE").replace("Ä","ae")
      if str(library["size_formatted"]) !=  "0\xa0Bytes":
       used = str(library["size_formatted"])
       used = str("".join(used.split())).replace(",",".")
       libraryConsumption += " " + label + "=" + str(used)

  except:
    print("UNKNOWN: no library found. Wrong token or adress!")
    sys.exit(UNKNOWN)
  return libraryConsumption
      
 #performance data

def quota_check(differ, percent, warn, crit, libraryConsumption):
  result = None
  if warn == 0:
        result = 0
        print('OK', abs((int(float(differ)/10**6))) , "MB quota used | quota="+str(abs((int(float(differ)/10**6))))+"MB"+ " " + libraryConsumption)
  else:
   if differ < crit:
    print('CRITICAL - less than', int(crit/10**6), "MB quota left (" +str((int(float(differ)/10**6))), "MB ", percent,"% free) | quota="+str((int(float(differ)/10**6)))+"MB;"+str(int(warn/10**6))+";"+str(int(crit/10**6))+ " " + libraryConsumption)
    result = 1
    sys.exit(CRITICAL)
   elif  differ < warn:
    print('WARNING - less than', int(warn/10**6), "MB quota left (" +str((int(float(differ)/10**6))), "MB ", percent,"% free) | quota="+str((int(float(differ)/10**6)))+"MB;"+str(int(warn/10**6))+";"+str(int(crit/10**6))+ " " + libraryConsumption)
    result = 1
    sys.exit(WARNING)
   else:
    result = 0
    print('OK', (int(float(differ)/10**6)) , "MB quota left, ("  +str((int(float(differ)/10**6))), "MB ", percent,"% free) | quota="+str((int(float(differ)/10**6)))+"MB;"+str(int(warn/10**6))+";"+str(int(crit/10**6))+ " " + libraryConsumption)
  return result

 # validate inpute and show usage
def command_line_validate(argv):
  try:
    opts, args = getopt.getopt(argv, 'w:c:t:a:o:', ['warn=' ,'crit=', 'tok=', 'adress='])

  except getopt.GetoptError:
    raise
    print(usage)

  try:
    for opt, arg in opts:
      if opt in ('-w', '--warn'):
        try:
          warn = int(arg)*10**6
        except:
          print('***warn value must be an integer***')
          sys.exit(CRITICAL)
      elif opt in ('-c', '--crit'):
        try:
          crit = int(arg)*10**6
        except:
          print('***crit value must be an integer***')
          sys.exit(CRITICAL)
      elif opt in ('-t', '--token'):
        try:
          tok = str(arg)
        except:
          print('***token is required***')
          sys.exit(CRITICAL)
      elif opt in ('-a', '--adress'):
        try:
          adress = str(arg)
        except:
          print('***adress is required***')
          sys.exit(CRITICAL)
                                      
                                      
      else:
        print(usage)
    try:
      isinstance(warn, int)
      #print 'warn level:', warn
    except:
      print('***warn level is required***')
      print(usage)
      sys.exit(CRITICAL)
    try:
      isinstance(crit, int)
      #print 'crit level:', crit
    except:
      print('***crit level is required***')
      print(usage)
      sys.exit(CRITICAL)
    try:
      isinstance(tok, int)
      #print 'crit level:', crit
    except:
       print('***token is required***')
       print(usage)
                    
  except:
    sys.exit(CRITICAL)
  # confirm that warning level is less than critical level, alert and exit if check fails
  if warn < crit:
    print('***warning level must be more than critical level***')
    sys.exit(CRITICAL)
  return warn, crit, tok, adress

# main function
def main():
  argv = sys.argv[1:]
  warn, crit, tok, adress = command_line_validate(argv)
  libraries = library_check(tok, adress)  
  differ, percent = used_quota(tok, adress)
  quota_check(differ,percent, warn, crit, libraries)


if __name__ == '__main__':
  main()
