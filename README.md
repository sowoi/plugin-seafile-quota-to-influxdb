# plugin-seafile-quota-to-influxdb
This standalone plugin creates metrics from Seafile libraries quotas and stores them in InfluxDB

# Prerequisites
- See requirements.txt
- Seafile API token
- InfluxDB token

# Poetry
`poetry install`


# Options
```
 -h, --help            show this help message and exit

  Generic options:
    -d, --debug         enable debugging outputs (default: no)

  Host options:
    -u URL, --url=URL   Seafile server address
    -s TOKEN, --seafiletoken=TOKEN
                        Seafile server token

  InfluxDB options:
    -H HOST, --host=HOST
                        InfluxDB Host (default: http://localhost)
    -p PORT, --port=PORT
                        InfluxDB Host (default: 8086)
    -t PORT, --token=PORT
                        InfluxDB Token (mandatory)
```

# Installation
See https://okxo.de/monitor-seafile-libraries-with-grafana/

# License
Licensed under the terms of Apache License Version 2. See LICENSE file.