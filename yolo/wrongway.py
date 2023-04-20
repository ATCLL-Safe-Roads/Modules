import asone
from asone import ASOne
import cv2
import os

from dotenv import load_dotenv

load_dotenv()

RTSP_URL = os.getenv('RTSP_URL')

def main():
    # Check for RTSP_URL environment variable
    if not RTSP_URL:
        print('Error: RTSP_URL environment variable not set (see README.md).')

    # Load tracker
    detect = ASOne(tracker=asone.BYTETRACK, detector=asone.YOLOV8N_PYTORCH, use_cuda=False)
    track = detect.track_stream(RTSP_URL, filter_classes=['car'], display=True, save_result=False)
    
    last_centers = {}
    
    # Loop over track to retrieve outputs of each frame
    for bbox_details, frame_details in track:
        bbox_xyxy, ids, scores, class_ids = bbox_details
        frame, frame_num, fps = frame_details
    
        n = len(ids)
    
        centers = {}
        # Draw center of bounding box on frame using cv
        for i in range(n):
            id = ids[i]
            x1, y1, x2, y2 = bbox_xyxy[i]
    
            center = (int((x1 + x2) // 2), int((y1 + y2) // 2))
            centers[id] = center
            cv2.circle(frame, center, 2, (0, 0, 255), -1)
        
        # Draw line a bit above the road axis
        p1 = (0, 240)
        p2 = (640, 25)
        cv2.line(frame, p1, p2, (0, 255, 0), 2)
    
        # Function representing the line
        def f(x):
            return ((p2[1]-p1[1])/(p2[0]-p1[0]))*x + p1[1]
    
        # Check for cars driving the wrong way
        for id, (x, y) in centers.items():
            if id not in last_centers:
                continue
            last_x, last_y = last_centers[id]
            if abs(last_x - x) < 5: # pixels
                continue
            if y < f(x) and last_x < x:
                print(f'car with id={id} driving in the wrong way')
            elif y > f(x) and last_x > x:
                print(f'car with id={id} driving in the wrong way')
        
        last_centers = centers
    
        # Display modifed frames
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

if __name__ == '__main__':
    main()