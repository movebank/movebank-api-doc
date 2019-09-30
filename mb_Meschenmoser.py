# Author: Philipp Meschenmoser, DBVIS, Uni Konstanz
# Python wrapper with functions using Movebank's REST API to view available studies, read data and accept license terms programmatically
# Acknowledgements to Anne K. Scharf and her great moveACC package, see https://gitlab.com/anneks/moveACC

import requests
import os
import hashlib
import csv
import json
import io
from datetime import datetime, timedelta

def callMovebankAPI(params):
    # Requests Movebank API with ((param1, value1), (param2, value2),).
    # Assumes the environment variables 'mbus' (Movebank user name) and 'mbpw' (Movebank password).
    # Returns the API response as plain text.

    response = requests.get('https://www.movebank.org/movebank/service/direct-read', params=params, auth=(os.environ['mbus'], os.environ['mbpw']))
    print("Request " + response.url)
    if response.status_code == 200:  # successful request
        if 'License Terms:' in str(response.content):
            # only the license terms are returned, hash and append them in a subsequent request.
            # See also
            # https://github.com/movebank/movebank-api-doc/blob/master/movebank-api.md#read-and-accept-license-terms-using-curl
            print("Has license terms")
            hash = hashlib.md5(response.content).hexdigest()
            params = params + (('license-md5', hash),)
            # also attach previous cookie:
            response = requests.get('https://www.movebank.org/movebank/service/direct-read', params=params,
                                    cookies=response.cookies, auth=(os.environ['mbus'], os.environ['mbpw']))
            if response.status_code == 403:  # incorrect hash
                print("Incorrect hash")
                return ''
        return response.content.decode('utf-8')
    print(str(response.content))
    return ''


def getStudies():
    studies = callMovebankAPI((('entity_type', 'study'), ('i_can_see_data', 'true'), ('there_are_data_which_i_cannot_see', 'false')))
    if len(studies) > 0:
        # parse raw text to dicts
        studies = csv.DictReader(io.StringIO(studies), delimiter=',')
        return [s for s in studies if s['i_can_see_data'] == 'true' and s['there_are_data_which_i_cannot_see'] == 'false']
    return []


def getStudiesBySensor(studies, sensorname='GPS'):
    return [s for s in studies if sensorname in s['sensor_type_ids']]


def getIndividualsByStudy(study_id):
    individuals = callMovebankAPI((('entity_type', 'individual'), ('study_id', study_id)))
    if len(individuals) > 0:
        return list(csv.DictReader(io.StringIO(individuals), delimiter=','))
    return []


def getIndividualEvents(study_id, individual_id, sensor_type_id=653):
    # See below table for sensor_type_id's.

    params = (('entity_type', 'event'), ('study_id', study_id), ('individual_id', individual_id),
              ('sensor_type_id', sensor_type_id), ('attributes', 'all'))
    events = callMovebankAPI(params)
    if len(events) > 0:
        return list(csv.DictReader(io.StringIO(events), delimiter=','))
    return []


def transformRawGPS(gpsevents):
    # Returns a list of (ts, deployment_id, lat, long) tuples

    def transform(e):  # dimension reduction and data type conversion
        try:
            if len(e['location_lat']) > 0:
                e['location_lat'] = float(e['location_lat'])
            if len(e['location_long']) > 0:
                e['location_long'] = float(e['location_long'])
        except:
            print("Could not parse long/lat.")
        return e['timestamp'], e['deployment_id'], e['location_lat'], e['location_long']

    return [transform(e) for e in gpsevents]



def transformRawACC(accevents, unit='m/s2', sensitivity = 'high'):
    #  Transforms raw tri-axial acceleration from X Y Z X Y X Y Z to [(ts_interpol, deployment, X', Y', Z'),...]
    #  X', Y', Z' are in m/s^2 or g. Assumes e-obs acceleration sensors.
    #  Acknowledgments to Anne K. Scharf and her great moveACC package, see https://gitlab.com/anneks/moveACC

    ts_format = '%Y-%m-%d %H:%M:%S.%f'
    out = []

    if unit == 'g':
        unitfactor = 1
    else:
        unitfactor = 9.81

    tag_local_identifier = int(accevents[0]['tag_local_identifier'])
    slope = 0.001  # e-obs 1st generation, high sensitivity

    if tag_local_identifier <= 2241:
        if sensitivity == 'low':
            slope = 0.0027
    elif 2242 <= tag_local_identifier <= 4117:  # e-obs 2nd generation
        slope = 0.0022
    else:
        slope = 1/512

    for event in accevents:
        deploym = event['deployment_id']
        seconds = 1/float(event['eobs_acceleration_sampling_frequency_per_axis'])
        parsedts = datetime.strptime(event['timestamp'], ts_format)  # start timestamp
        raw = list(map(int, event['eobs_accelerations_raw'].split()))

        #  derive in-between timestamps:
        ts = [parsedts + timedelta(seconds=seconds * x) for x in range(0, int(len(raw)/3))]

        #  transform XYZ list to list of (ts, deployment, x, y, z) tuples
        it = iter(raw)
        transformed = [(a.strftime(ts_format), deploym,  (b[0]-2048)*slope*unitfactor, (b[1]-2048)*slope*unitfactor,
                        (b[2]-2048)*slope*unitfactor) for (a, b) in list(zip(ts, list(zip(it, it, it))))]
        out.append(transformed)
    return out


def prettyPrint(l):
    print(json.dumps(l, indent=2))


if __name__ == "__main__":
    allstudies = getStudies()

    gpsstudies = getStudiesBySensor(allstudies, 'GPS')
    prettyPrint(gpsstudies)

    individuals = getIndividualsByStudy(study_id=9493874)
    prettyPrint(individuals)

    gpsevents = getIndividualEvents(study_id=9493874, individual_id=11522613, sensor_type_id=653) #GPS events
    if len(gpsevents) > 0:
        prettyPrint(transformRawGPS(gpsevents))

    # Print tri-axial acceleration in m/s^2: [(ts, deployment, accx, accy, accz), [ts,...],...]
    accevents = getIndividualEvents(study_id=9493874, individual_id=11522613, sensor_type_id=2365683) #ACC events
    if len(accevents) > 0:
        prettyPrint(transformRawACC(accevents))



""""
SENSORS
===============================================================================
description,external_id,id,is_location_sensor,name
"","bird-ring",397,true,"Bird Ring"
"","gps",653,true,"GPS"
"","radio-transmitter",673,true,"Radio Transmitter"
"","argos-doppler-shift",82798,true,"Argos Doppler Shift"
"","natural-mark",2365682,true,"Natural Mark"
"","acceleration",2365683,false,"Acceleration"
"","solar-geolocator",3886361,true,"Solar Geolocator"
"","accessory-measurements",7842954,false,"Accessory Measurements"
"","solar-geolocator-raw",9301403,false,"Solar Geolocator Raw"
"","barometer",77740391,false,"Barometer"
"","magnetometer",77740402,false,"Magnetometer"
"","orientation",819073350,false,"Orientation"
"","solar-geolocator-twilight",914097241,false,"Solar Geolocator Twilight"
"""

