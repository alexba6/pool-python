from network import WLAN

from models.wifi_app import WifiApp
from tools.database import Database, Repository

STAT_IDLE = 1000
STAT_CONNECTING = 1001
STAT_WRONG_PASSWORD = 202
STAT_NO_AP_FOUND = 201
STAT_GOT_IP = 1010

AUTH_MODE = ['Open', 'WEP', 'WPA-PSK' 'WPA2-PSK4', 'WPA/WPA2-PSK']


class Wifi:
    wlan: WLAN
    current_app: WifiApp or None
    repo: Repository

    def __init__(self, db: Database):
        self.wlan = WLAN(0)
        self.wlan.active(True)
        self.current_app = None
        self.repo = db.get_repository(WifiApp)

    def connect(self, wifi_app: WifiApp):
        print('Connecting to {} - pass {}'.format(wifi_app.ssid, wifi_app.password))
        self.wlan.connect(wifi_app.ssid, wifi_app.password)
        self.current_app = wifi_app

    def disconnect(self):
        self.wlan.disconnect()
        self.current_app = None

    def connect_best(self):
        for (ssid, bssid, channel, RSSI, auth_mode, hidden) in self.wlan.scan():
            wifi_app = self.repo.find('ssid', ssid.decode())
            if wifi_app:
                self.connect(wifi_app)
                return
