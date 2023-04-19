#{
#    "id": "int",
#    "type": "str",
#    "source": "str",
#    "sourceid": "int",
#    "description": "str",
#    "location": "str",
#    "points": "lst",
#    "start": "datetime",
#    "end": "datetime",
#    "timestamp": "datetime"
#}

def eventEntity(event) -> dict:
    return {
        "id": str(event["id"]),
        "type": event["type"],
        "source": event["source"],
        "sourceid": event["sourceid"],
        "description": event["description"],
        "location": event["location"],
        "points": event["points"],
        "start": event["start"],
        "end": event["end"],
        "timestamp": event["timestamp"]
    }