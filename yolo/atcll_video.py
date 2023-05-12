import click
import cv2
import os

from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

MODEL_PATH = 'runs/detect/train/weights/last.pt'
RTSP_URL = os.getenv('RTSP_URL')


@click.command()
@click.option('--detect', type=click.Choice(['pothole']), required=True)
def main(detect):
    # Check for RTSP_URL environment variable
    if not RTSP_URL:
        print('Error: RTSP_URL environment variable not set (see README.md).')

    # Load the model
    model = YOLO(f'./{detect}/{MODEL_PATH}')

    # Connect to RTSP stream
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print('Error: Unable to open RTSP stream.')
        return

    while True:
        _, frame = cap.read()

        results = model(frame)[0]

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > 0.5:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(frame, f'{score:.2f} - {class_id}', (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)

        cv2.imshow('RTSP Stream - Press ESC to exit', frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
