import requests
import re

def get_all_stations():
    s = requests.Session()
    tmp = s.get("https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_fr.txt")
    descriptionLines = tmp.text.split('\n')
    cordinatesFound = False
    stationList = {}
    for line in descriptionLines:
        if not cordinatesFound :
            if(re.match(r"Stations\sCoordinates", line)):
                cordinatesFound = True
        else:
            if(re.match(r"[A-Z]{3}\s+",line)):
                lineParts = re.split(r'\s\s+',line)
                stationList["code"] = lineParts[0]
                
                ## Saving station data to a dictionnary
                stationData = {}
                stationData["name"] = lineParts[1]
                stationData["altitude"] = lineParts[4].strip()

                stationList[lineParts[0]] = stationData
    return stationList             