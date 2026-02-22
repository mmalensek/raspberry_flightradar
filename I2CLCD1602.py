#!/usr/bin/env python3

import os
from time import sleep, strftime
import smbus
from datetime import datetime
import requests
from LCD1602 import CharLCD1602
from dotenv import load_dotenv

lcd1602 = CharLCD1602()

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("Warning: API_KEY not found")
LJLJ = 'LJLJ' # change later to LJLJ

# get system time
def get_time_now():
    return datetime.now().strftime('    %H:%M:%S')

def get_next_flight():
    try:
        url = f"https://airlabs.co/api/v9/flights?api_key={API_KEY}&arr_icao={LJLJ}&dep_icao={LJLJ}&status=en-route,landed&_fields=flight_number,status,updated&_view=array&limit=10"
        print(f"URL: {url[:100]}...")  # Truncate for security
        print(f"API_KEY loaded: {'Yes' if API_KEY else 'No'}")
        resp = requests.get(url, timeout=10)
        print(f"Status code: {resp.status_code}")
        print(f"Response headers: {dict(resp.headers)}")
        print(f"Raw response: {resp.text[:500]}")  # First 500 chars
        
        if resp.status_code != 200:
            print(f"HTTP error: {resp.status_code}")
            return f"HTTP {resp.status_code}"
            
        data = resp.json().get('response', [])
        print(f"Data length: {len(data)}")
        
        if len(data) > 0:
            data.sort(key=lambda x: x.get('updated', 0), reverse=True)
            flight = data[0]
            num = flight.get('flight_number', 'UNK')
            status = flight.get('status', '').upper()
            return f"{num} {status[:4]}"
        return "No traffic"
    except requests.exceptions.Timeout:
        return "Timeout"
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "Net error"
    except ValueError as e:  # JSON decode fail
        print(f"JSON error: {e}")
        return "JSON error"
    except Exception as e:
        print(f"Other error: {type(e).__name__}: {e}")
        return "Other error"


# display refreshes every 5 min to save API calls ~9000/month
FLIGHT_UPDATE_INTERVAL = 300  # seconds
last_update = 0

def loop():
    lcd1602.init_lcd()
    while(True):
        
        global last_update
        
        now = datetime.now()
        if (now - datetime.fromtimestamp(last_update)).total_seconds() > FLIGHT_UPDATE_INTERVAL:
            last_update = now.timestamp()
            print("Requesting data from API ... ")
            lcd1602.clear()
            lcd1602.write(0, 0, get_next_flight())  # next landing/departing
            lcd1602.write(0, 1, get_time_now() )    # time

def destroy():
    lcd1602.clear()

if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
