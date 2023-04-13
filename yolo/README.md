# PI Project - YOLO Module

## Description

This module contains training data and scripts to support the development of YOLOv8 models and methods to detect events from video footage.

## Contents

- `atcll_video.py` - Connects to a remote camera using RTSP and executes one of the trained models to each frame, outputing the frames with the bounding boxes.
  
  - `--detect` - model to execute on the frames (`pothole`).

## Installation

- Run `pip3 install virtualenv` to install the module `virtualenv`.
- Run `virtualenv venv` in root to create a virtual environment.
- Run `source venv/bin/activate` in root to enter the virtual environment.
- Run `pip3 install -r requirements.txt` to install all dependencies.

## Environment Variables

Some scripts some environment variables to be set. It is recommended to add an `.env` file in the same directory as the script contaning the required variables.

- `atcll_video.py`
  
  - `RTSP_URL` - of the camera to connect to.

## Authors

- João Fonseca, 103154
