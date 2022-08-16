import services.web_socket
import services.wifi
import services.pump

import tools.temperature
import tools.loop
import tools.schedule


from app import ws_client, pump, wifi, water_temperature, ds, outside_temperature

import events.action
import events.slot

water_temperature.init()
outside_temperature.init()
pump.init()

loop = tools.loop.Loop()
schedule = tools.schedule.Schedule(ds)

loop.add_callback(name='pump', period=250, callback=lambda: pump.loop())
loop.add_callback(name='water_temperature', period=500, callback=lambda: water_temperature.loop())
loop.add_callback(name='outside_temperature', period=500, callback=lambda: outside_temperature.loop())
loop.add_callback(name='refresh_temperature', period=500, callback=lambda: tools.temperature.refresh_temperature())
loop.add_callback(name='socket', callback=lambda: ws_client.loop())
loop.add_callback(name='schedule', period=250, callback=lambda: schedule.loop())


@schedule.add((0, 0, 0), name='end_day')
def end_day():
    pump.end_day()


@loop.add(name='check_network', period=1500)
def check_network():
    wlan_status = wifi.wlan.status()
    if wlan_status != services.wifi.STAT_CONNECTING and wlan_status != services.wifi.STAT_GOT_IP:
        try:
            wifi.connect_best()
        except Exception as e:
            print('wifi error', e)
    elif wlan_status == services.wifi.STAT_GOT_IP:
        socket_status = ws_client.status
        if socket_status == services.web_socket.CLOSED or socket_status == services.web_socket.IDLE:
            ws_client.connect()


while True:
    loop.loop()
