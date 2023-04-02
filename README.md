# USAGE

Copy this code your HA config/custom_components/toshiba_ac

# CONFIGURATION

Add in your configuration.yaml this extension with parameters to access your device.

```
toshiba_ac:
climate:
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  name: "Toshiba AC Evelyne"
  ip: <device_ip_in_local_network>
  localkey: <id as found by tuya app developer sdk>
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  name: "Toshiba AC Garcons"
  ip: <device_ip_in_local_network>
  localkey: <id as found by tuya app developer sdk>
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  name: "Toshiba AC Parents"
  ip: <device_ip_in_local_network>
  localkey: <id as found by tuya app developer sdk>
  ...
sensor:
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  climate: climate.toshiba_ac_<roomname>
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  climate: climate.toshiba_ac_garcons
- platform: toshiba_ac
  id: <id as found by tuya app developer sdk>
  climate: climate.toshiba_ac_parents
  ...
```

NOTE: There are probably better ways to solve it or implenment it, feel free to use it.
