# PI Project - YOLO Module

## Description

This module contains training data and scripts to support the development of YOLOv8 models and methods to detect events from video footage.

## Contents

- `atcll_video.py` - Connects to a remote camera using RTSP and executes one of the trained models to each frame, outputing the frames with the bounding boxes.
  
  - `--detect` - model to execute on the frames (`pothole`).

- `atcll_image.py` - Connects to a remove camera using RTSP, capturing frames at a given rate and saving them to an output folder.
  
  - `--n` - number of frames to capture.
  
  - `--rate` - interval between each captured frame.

- `wrong_way.py` - Connects to a remote camera using RTSP and tracks cars using YOLOv8n, to detect cars driving the wrong way based on an axis and their position.

## Installation

- Run `pip3 install virtualenv` to install the module `virtualenv`.
- Run `virtualenv venv` in root to create a virtual environment.
- Run `source venv/bin/activate` in root to enter the virtual environment.
- Run `pip3 install -r requirements.txt` to install all dependencies.

## Environment Variables

Some scripts some environment variables to be set. It is recommended to add an `.env` file in the same directory as the script contaning the required variables.

- `atcll_image.py`, `atcll_video.py` & `wrong_way.py`
  
  - `RTSP_URL` - of the camera to connect to.

## Authors

- João Fonseca, 103154
