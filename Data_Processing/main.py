import mqtt
import time
from threading import Thread
from traffic_flow_here import fetch_tf_here
from traffic_incidents_here import fetch_ti_here


class Broker(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt.Consumer().run()


if __name__ == "__main__":
    broker = Broker()
    broker.start()

    while True:
        # fetch incidents from HERE
        st = fetch_ti_here()
        # if st == 0:
        #    print("HERE_ti - OK")
        # else:
        #    print("HERE_ti - ERROR")

        ## fetch traffic flow from HERE
        st = fetch_tf_here()
        # if st == 0:
        #    print("HERE_tf - OK")
        # else:
        #    print("HERE_tf - ERROR")
        ## TODO - CHANGE TO MORE APPROPRIATE TIME
        time.sleep(10)
        pass
