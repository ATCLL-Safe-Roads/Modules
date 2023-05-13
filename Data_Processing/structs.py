class Event:
    counter = 0

    def __init__(self, type, source, description, location, geometry, start, end, timestamp):
        self.type = type
        self.source = source
        self.sourceid = Event.counter
        self.description = description
        self.location = location
        self.geometry = geometry
        self.start = start
        self.end = end
        self.timestamp = timestamp
        Event.counter += 1


class Flow:
    counter = 0

    def __init__(self, source, location, avgspeed, segments, timestamp):
        self.source = source
        self.location = location
        self.avgspeed = avgspeed
        self.segments = segments
        self.timestamp = timestamp
        Flow.counter += 1
