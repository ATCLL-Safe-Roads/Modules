#{
#    "id": "int",
#    "source": "str",
#    "location": "str",
#    "avgspeed": "float",
#    "length": "float",
#    "segments": [
#        {
#            "speed": "float",
#            "length": "float",
#            "points": [
#                {
#                    "lat": "double",
#                    "lon": "double"
#                },
#                {
#                    "lat": "double",
#                    "lon": "double"
#                },
#                ...
#            ]
#        },
#        ...
#    ],
#    "timestamp": "datetime"
#}

def flowEntity(flow) -> dict:
    return {
        "id": str(flow["id"]),
        "source": flow["source"],
        "location": flow["location"],
        "avgspeed": flow["avgspeed"],
        "length": flow["length"],
        "segments": flow["segments"],
        "timestamp": flow["timestamp"]
    }