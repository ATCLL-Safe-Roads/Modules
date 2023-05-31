import cv2
import os

from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = 'runs/detect/train/weights/last.pt'
RTSP_URL = os.getenv('RTSP_URL')


def main():
    # Check for RTSP_URL environment variable
    if not RTSP_URL:
        print('Error: RTSP_URL environment variable not set (see README.md).')

    # Connect to RTSP stream
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print('Error: Unable to open RTSP stream.')
        return

    width = int(cap.get(3))
    height = int(cap.get(4))

    print(f'Info: RTSP stream {width}x{height} @ {RTSP_URL}')

    while True:
        _, frame = cap.read()

        cv2.imshow('RTSP Stream - Press ESC to exit', frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
