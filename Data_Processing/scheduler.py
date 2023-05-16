import schedule
import time

from threading import Thread


class Scheduler(Thread):
    def __init__(self, pothole_service, fetch_ti_here, fetch_tf_here):
        super().__init__()
        schedule.every().day.at('13:00').do(pothole_service.check_potholes)
        schedule.every().minute.at(':00').do(fetch_ti_here)
        schedule.every().minute.at(':30').do(fetch_ti_here)
        schedule.every().minute.at(':00').do(fetch_tf_here)
        schedule.every().minute.at(':30').do(fetch_tf_here)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
