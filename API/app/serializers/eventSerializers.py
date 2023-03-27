#{
#    "id": "int",
#    "type": "str",
#    "source": "str",
#    "description": "str",
#    "location": "str",
#    "start": "datetime",
#    "end": "datetime",
#    "timestamp": "datetime"
#}

def eventEntity(event) -> dict:
    return {
        "id": str(event["_id"]),
        "type": event["type"],
        "source": event["source"],
        "sourceid": event["sourceid"],
        "description": event["description"],
        "location": event["location"],
        "start": event["start"],
        "end": event["end"],
        "timestamp": event["timestamp"]
    }