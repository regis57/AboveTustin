#
# flightdata.py
#
# kevinabrandon@gmail.com
#


from urllib.request import urlopen
import json
from time import sleep
import geomath
import math
from datetime import datetime
from dateutil import tz

DUMP1090DATAURL = "http://192.168.0.101/dump1090/data/aircraft.json"
myLoc = (33.754271, -117.823096)
myTz = tz.gettz('America/Los_Angeles')
utcTz = tz.gettz('UTC')

class FlightData():
    def __init__(self, data_url = DUMP1090DATAURL):

        self.data_url = data_url
        self.aircraft = None

        self.refresh()

    def refresh(self):
        #open the data url
        self.req = urlopen(self.data_url)

        #read data from the url
        self.raw_data = self.req.read()

        #load in the json
        self.json_data = json.loads(self.raw_data.decode())

        #get time from json and convert to our time zone
        self.time = datetime.fromtimestamp(self.json_data["now"])
        self.time = self.time.replace(tzinfo=utcTz)
        self.time = self.time.astimezone(myTz)

        #load all the aircarft
        self.aircraft = AirCraftData.parse_flightdata_json(self.json_data, self.time)

class AirCraftData():
    def __init__(self,
                 dhex,
                 squawk,
                 flight,
                 lat,
                 lon,
                 altitude,
                 vert_rate,
                 track,
                 speed,
                 messages,
                 seen,
                 mlat,
                 nucp,
                 seen_pos,
                 rssi,
                 dist, 
                 az,
                 el,
                 time):
        
        self.hex = dhex
        self.squawk = squawk
        self.flight = flight
        self.lat = lat
        self.lon = lon
        self.altitude = altitude
        self.vert_rate = vert_rate
        self.track = track
        self.speed = speed
        self.messages = messages
        self.seen = seen
        self.mlat = mlat
        self.nucp = nucp
        self.seen_pos = seen_pos
        self.rssi = rssi
        self.distance = dist
        self.az = az
        self.el = el
        self.time = time

    @staticmethod
    def parse_flightdata_json(json_data, time):
        aircraft_list = []
        for a in json_data["aircraft"]:

            alt = a["altitude"] if "altitude" in a else 0
            if alt == "ground":
                alt = 0
            dist = -1
            az = 0
            el = 0
            if "lat" in a and "lon" in a:
                dist = geomath.distance(myLoc, (a["lat"], a["lon"]))
                az = geomath.bearing(myLoc, (a["lat"], a["lon"]))
                el = math.degrees(math.atan(alt / (dist*5280)))
            speed = 0
            if "speed" in a:
                speed = geomath.knot2mph(a["speed"])

            aircraftdata = AirCraftData(
                a["hex"] if "hex" in a else None,
                a["squawk"] if "squawk" in a else None,
                a["flight"] if "flight" in a else "N/A",
                a["lat"] if "lat" in a else None,
                a["lon"] if "lon" in a else None,
                alt,
                a["vert_rate"] if "vert_rate" in a else 0,
                a["track"] if "track" in a else None,
                speed,
                a["messages"] if "messages" in a else None,
                a["seen"] if "seen" in a else None,
                a["mlat"] if "mlat" in a else None,
                a["nucp"] if "nucp" in a else None,
                a["seen_pos"] if "seen_pos" in a else None,
                a["rssi"] if "rssi" in a else None,
                dist,
                az,
                el,
                time)

            aircraft_list.append(aircraftdata)
        return aircraft_list


if __name__ == "__main__":
    
    import os
    import datetime

    flightdata = FlightData()
    while True:
        os.system('clear')
        print("Now: {}".format(datetime.datetime.fromtimestamp(int(flightdata.time)).strftime('%Y-%m-%d %H:%M:%S')))
        print("|  icao   | flight  | miles |   az  |  el  |  alt  | mi/h  | vert  | rssi  | mesgs | seen |")
        print("|---------+---------+-------+-------+------+-------+-------+-------+-------+-------+------|")
        sortedlist = []
        for a in flightdata.aircraft:
            if a.lat == None or a.lon == None:
                continue
            sortedlist.append(a)
        
        sortedlist.sort(key=lambda x: x.distance) # actually do the sorting here

        for a in sortedlist:
            print("| {:<7} | {:^8}| {:>5} | {:>5} | {:>4} | {:>5} | {:>5} | {:>+5} | {:>5} | {:>5} | {:>4} |".format(
                a.hex, 
                a.flight, 
                "%.1f" % a.distance,
                "%.1f" % a.az,
                "%.1f" % a.el,
                a.altitude, 
                "%.1f" % a.speed,
                a.vert_rate,
                "%0.1f" % a.rssi,
                a.messages,
                "%.1f" % a.seen))
        sleep(0.5)
        flightdata.refresh()
