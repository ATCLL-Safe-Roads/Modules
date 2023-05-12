import click
import cv2
import os
import time

from dotenv import load_dotenv

load_dotenv()

RTSP_URL = os.getenv('RTSP_URL')
OUT_FOLDER = 'atcll_image_out'

@click.command()
@click.option('--n', type=int, help='Number of images', required=True)
@click.option('--rate', type=int, help='Rate of capture in seconds', required=True)
def main(n, rate):
    # Check for RTSP_URL environment variable
    if not RTSP_URL:
        print('Error: RTSP_URL environment variable not set (see README.md).')

    # Connect to RTSP stream
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print('Error: Unable to open RTSP stream.')
        return

    if not os.path.exists(OUT_FOLDER):
        os.makedirs(OUT_FOLDER)

    i = 0
    prev_ts = time.time()
    while True:
        _, frame = cap.read()
        curr_ts = time.time()
        if curr_ts - prev_ts > rate:
            cv2.imwrite(f'{OUT_FOLDER}/out_{i}.jpg', frame)
            print(f'Captured frame {i}')
            prev_ts = curr_ts
            i += 1
            if i == n:
                break

    cap.release()


if __name__ == '__main__':
    main()
