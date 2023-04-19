import mqtt
import json
import requests
import datetime

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN
FLOW_URL = 'https://data.traffic.hereapi.com/v7/flow'

cache = []


def get_segments(subsegments, shapes):
    segments = []

    for seg in subsegments:
        length = seg["length"]

        lp = []

        lt = 0
        while lt < length:
            if len(shapes) == 0:
                break
            # Check if the next length passes the segment
            if lt + shapes[0]["length"] > length + 5:
                if len(shapes) == 1:
                    # If it's the last shape, just add it
                    lp.append(shapes[0])
                break
            pr = shapes.pop(0)
            lp.append(pr)
            lt += pr["length"]

        jf = 0.0
        jamtemp = seg["jamFactor"]
        if jamtemp <= 10/3:
            jf = 1.0
        elif jamtemp <= 20/3:
            jf = 2.0
        else:
            jf = 3.0


        msg = {
            "jamFactor": jf,
            "points": lp
        }

        segments.append(msg)
    return segments

def fetch_tf_here():
    # radial area => (lat, lon, radius) in meters 
    # can also be done by bounding box => {west longitude},{south latitude},{east longitude},{north latitude}

    # Aveiro
    lat = 40.63733
    lon = -8.64850
    rad = 500  # meters

    # these params -> https://developer.here.com/documentation/traffic-api/api-reference.html
    params = {
        'apiKey': API_KEY,
        'locationReferencing': 'shape', # 'shape', 'none', 'olr', 'tmc'     
                                        # -> shape will give us a lot of coords
        'in': f'circle:{lat},{lon};r={rad}' # radial area => (lat, lon, radius) in meters
    }
    tf_here = requests.get(url=FLOW_URL, params=params).json()
    
    for flow in tf_here["results"]:

        if "subSegments" in flow['currentFlow']:
            subSegments = flow['currentFlow']['subSegments']
            shapes = flow['location']['shape']['links']
            msg = {
                "source": "HERE",
                "location": flow['location']['description'],
                "avgspeed": flow['currentFlow']['speedUncapped'],
                "segments": get_segments(subSegments, shapes),
                "timestamp": tf_here['sourceUpdated']
            }
        else:
            jf = 0.0
            jamtemp = flow['currentFlow']['jamFactor']
            if jamtemp <= 10 / 3:
                jf = 1.0
            elif jamtemp <= 20 / 3:
                jf = 2.0
            else:
                jf = 3.0
            s = {
                "jamFactor": jf,
                "points": flow['location']['shape']['links']
            }
            msg = {
                "source": "HERE",
                "location": flow['location']['description'],
                "avgspeed": flow['currentFlow']['speedUncapped'],
                "segments": [s],
                "timestamp": tf_here['sourceUpdated']
            }

        if msg not in cache:
            cache.append(msg)
            # print msg
            print(json.dumps(msg, indent=4, default=str))
            # publish the data to the IT broker topic /traffic-flow-here
            Producer = mqtt.Producer()
            # print(type(msg))
            topic = "/traffic-flow-here"
            status = 0  # 0 = success, 1 = failure
            status = Producer.publish(json.dumps(msg,default=str), topic)
            if status == 0:
                print(f"Message SUCCESSFULLY SENT!")
            else:
                print(f"Failed to send message to topic {topic}")
        else:
            print("Message already in cache")
    


    #return status

