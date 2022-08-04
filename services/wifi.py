from network import WLAN

from tools.config import Config

STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = 2
STAT_NO_AP_FOUND = 3
STAT_CONNECT_FAIL = 4
STAT_GOT_IP = 5


class WifiApp:
    ssid: str
    password: str or None

    def __init__(self, ssid: str, password: str or None = None):
        self.ssid = ssid
        self.password = password


class Wifi(Config):
    wlan: WLAN
    current_app: WifiApp or None

    def __init__(self):
        super().__init__('wifi')
        self.wlan = WLAN(0)
        self.current_app = None
        self.load_config()

    def connect(self, wifi_app: WifiApp):
        self.wlan.active(True)
        self.wlan.connect(wifi_app.ssid, wifi_app.password)
        self.current_app = wifi_app

    def disconnect(self):
        self.wlan.disconnect()
        self.current_app = None

    def get_saved_wifi_apps(self):
        networks = self.config.get('networks')
        return [WifiApp(network.get('ssid'), network.get('password')) for network in networks]

    def connect_best(self):
        wifi_apps = self.get_saved_wifi_apps()
        if len(wifi_apps) > 0:
            self.connect(wifi_apps[0])
