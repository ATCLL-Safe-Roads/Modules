from ultralytics import YOLO


def main():
    # Load model
    model = YOLO('yolov8n.yaml')

    # Use model
    results = model.train(data='config.yaml', epochs=100)


if __name__ == '__main__':
    main()
