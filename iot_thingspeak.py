# iot_thingspeak.py
import network, time
import urequests

SSID = "WIFI_KAMU"
PASS = "PASSWORD_KAMU"
API_KEY = "APIKEY_THINGSPEAK"

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASS)
        for _ in range(40):
            if wlan.isconnected():
                break
            time.sleep(0.25)
    return wlan.isconnected()

def send_event(distance_cm, danger):
    # field1=distance, field2=danger(0/1)
    url = "https://api.thingspeak.com/update"
    params = "?api_key={}&field1={}&field2={}".format(API_KEY, distance_cm or -1, 1 if danger else 0)
    try:
        r = urequests.get(url + params)
        r.close()
        return True
    except:
        return False
