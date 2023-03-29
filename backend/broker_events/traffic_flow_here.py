import mqtt
import json
import requests

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN
FLOW_URL = 'https://data.traffic.hereapi.com/v7/flow'


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

        msg = {
            "speed": seg["speedUncapped"] * 3.6,
            "jamFactor": seg["jamFactor"],
            "length": length,
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
    tf_here = requests.get(url=FLOW_URL, params=params)

    id = 0
    idf = 0
    lst = []
    
    for flow in tf_here["results"]:
        
        if "subSegments" in flow['currentFlow']:

            subSegments = flow['currentFlow']['subSegments']
            shapes = flow['location']['shape']['links']

            msg = {
                "id": idf + 1,
                "source": "HERE",
                "location": flow['location']['description'],
                "avgspeed": flow['currentFlow']['speedUncapped'],
                "length": flow['location']['length'],
                "segments": get_segments(subSegments, shapes),
                "timestamp": tf_here['sourceUpdated']
            }
            idf += 1
            lst.append(msg)
        else:
            s = {
                "speed": flow['currentFlow']['speedUncapped'] * 3.6,
                "jamFactor": flow['currentFlow']['jamFactor'],
                "length": flow['location']['length'],
                "points": flow['location']['shape']['links']
            }

            msg = {
                "id": idf + 1,
                "source": "HERE",
                "location": flow['location']['description'],
                "avgspeed": flow['currentFlow']['speedUncapped'],
                "length": flow['location']['length'],
                    "segments": [s],
                "timestamp": tf_here['sourceUpdated']
            }
            idf += 1
            lst.append(msg)


        # print lst
        print(json.dumps(msg, indent=4))
        # publish the data to the IT broker topic /traffic-flow-here
        Producer = mqtt.Producer()
        # print(type(msg))
        topic = "/traffic-flow-here"
        status = 0  # 0 = success, 1 = failure
        status = Producer.publish(json.dumps(msg), topic)
        if status == 0:
            print(f"Message SUCCESSFULLY SENT!")
            print(f"Message ID: {id}")
            id += 1
        else:
            print(f"Failed to send message to topic {topic}")
    


    return status

