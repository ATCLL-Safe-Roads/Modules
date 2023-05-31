import schedule
import time

from threading import Thread

from here_api_service import HereApiService
from pothole_service import PotholeService


class Scheduler(Thread):
    def __init__(self, here_api_service: HereApiService, pothole_service: PotholeService):
        super().__init__()
        schedule.every().hour.at(':00').do(here_api_service.fetch_and_publish_data)
        schedule.every().hour.at(':30').do(here_api_service.fetch_and_publish_data)
        schedule.every().day.at('13:00').do(pothole_service.check_potholes)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
