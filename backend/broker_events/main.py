import mqtt
from threading import Thread


class Broker(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt.Consumer().run()


if __name__ == "__main__":
    broker = Broker()
    broker.start()
