import cv2
import os

from ultralytics import YOLO

MODEL_PATH = 'runs/detect/train/weights/last.pt'
VIDEOS_DIR = 'videos'


def main():
    # Load the model
    model = YOLO(MODEL_PATH)

    # Apply the model to each video
    for video in os.listdir(VIDEOS_DIR):

        cap = cv2.VideoCapture(f'{VIDEOS_DIR}/{video}')
        ret, frame = cap.read()
        H, W, _ = frame.shape
        out = cv2.VideoWriter(f'{VIDEOS_DIR}/{video.rsplit(".")[0]}_out.mp4', cv2.VideoWriter_fourcc(*'MP4V'),
                              int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

        while True:

            results = model(frame)[0]

            for result in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result

                if score > 0.5:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                    cv2.putText(frame, f'{score:.2f} - {class_id}', (int(x1), int(y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)

            out.write(frame)
            ret, frame = cap.read()
            if not ret:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
