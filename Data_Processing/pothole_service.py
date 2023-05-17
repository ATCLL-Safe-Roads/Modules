import cv2
import json
import math
import os

from datetime import datetime, timedelta
from dotenv import load_dotenv
from threading import Thread
from typing import Set, Dict, List, Tuple
from ultralytics import YOLO

from mqtt import Producer
from structs import Event
from utils import get_pixel_to_coordinates_table

CHECK_DURATION = 10  # seconds
CONFIDENCE_THRESHOLD = 0.7
DISTANCE_THRESHOLD = 50  # pixels

PATH = os.path.dirname(__file__)

load_dotenv(os.path.join(PATH, '', '.env'))


class PotholeService:

    def __init__(self, p_ids: Set[int], p_names: Dict[int, str], p_points: Dict[int, Tuple[float, float]],
                 mqtt_producer: Producer):
        self.p_ids = p_ids
        self.p_names = p_names
        self.p_points = p_points
        self.mqtt_producer = mqtt_producer

        # Load RTSP URLs
        self.p_rtsp_urls = {}
        for p_id in p_ids:
            p_rtsp_url = os.getenv(f'ATCLL_P{p_id}_RTSP_URL')
            if p_rtsp_url:
                self.p_rtsp_urls[p_id] = p_rtsp_url
        print(f'INFO: Monitoring potholes near SLPs with ids {set(self.p_rtsp_urls.keys())}.')
        # Check for untracked SLPs
        up_ids = self.p_ids - set(self.p_rtsp_urls.keys())
        if up_ids:
            print(f'WARN: No ATCLL_P{{id}}_RTSP_URL environment variable set for SLPs with ids {up_ids}. '
                  f'These SLPs will not be monitored for potholes.')
            self.p_ids = p_ids - up_ids
            self.p_names = {p_id: p_name for p_id, p_name in p_names.items() if p_id in self.p_ids}

        # Load YOLOv8n model
        self.model = YOLO(os.path.join(PATH, 'pothole_model.pt'))

        # Load pixel to coordinates tables
        self.p_ptc_tables = {}
        for p_id in self.p_ids:
            ptc_table = get_pixel_to_coordinates_table(p_id)
            if not ptc_table:
                print(f'WARN: Unable to load pixel to coordinates table for SLP with id {p_id}. '
                      f'Pothole coordinates will default to the SLP coordinates.')
            self.p_ptc_tables[p_id] = ptc_table

    def check_potholes(self):
        tt = []
        # Create a thread for each SLP
        for p_id in self.p_ids:
            t = Thread(target=self.__check, args=(p_id,))
            tt.append(t)
        # Start all threads
        for t in tt:
            t.start()
        # Wait for all threads to finish
        for t in tt:
            t.join()
        print('INFO: Pothole check finished.')

    def __check(self, p_id):
        print(f'INFO: Checking for potholes near SLP with id {p_id}.')

        # Connect to RTSP stream
        cap = cv2.VideoCapture(self.p_rtsp_urls[p_id])
        if not cap.isOpened():
            print(f'ERROR: Unable to open RTSP stream for SLP with id {p_id}.')
            return

        detections = []  # List of detections for future filtering
        start_ts = datetime.now()
        while True:
            # Read frame from RTSP stream
            _, frame = cap.read()

            # Detect potholes
            results = self.model.predict(source=frame, verbose=False)[0]

            # Check for potholes
            for result in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result

                if score > CONFIDENCE_THRESHOLD:
                    position = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    detections.append((position, score))

            # Exit if CHECK_DURATION seconds have passed
            if datetime.now() - start_ts > timedelta(seconds=CHECK_DURATION):
                break

        cap.release()

        # Remove duplicate detections
        if detections:
            filtered_detections = [detections[0]]
            for d in detections[1:]:
                # Compare detection with all filtered detections
                for i in range(0, len(filtered_detections)):
                    fd = filtered_detections[i]
                    # Detection can be considered to be the same if it is close enough
                    if math.dist(d[0], fd[0]) < DISTANCE_THRESHOLD:
                        # Keep detection with higher score
                        if d[1] > fd[1]:
                            filtered_detections[i] = d
                        break
                else:
                    filtered_detections.append(d)
            # Create event for each detection
            for fd in filtered_detections:
                lat, lng = self.p_ptc_tables[p_id][fd[0][0]][fd[0][1]] \
                    if self.p_ptc_tables[p_id] else self.p_points[p_id]
                now_ts = datetime.now()
                event = Event(
                    type='pothole',
                    source='atcll',
                    description=f'Pothole detected near SLP with id {p_id} with a confidence of {100 * fd[1]:.2f}%.',
                    location=self.p_names[p_id],
                    geometry=[{'points': [{'lat': lat, 'lng': lng}]}],
                    start=str(now_ts.isoformat()),
                    end=str((now_ts + timedelta(days=1)).isoformat()),
                    timestamp=str(now_ts),
                )
                self.mqtt_producer.publish(json.dumps(event.__dict__), topic='/events')
