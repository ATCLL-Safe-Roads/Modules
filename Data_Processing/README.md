# ATCLL - Safe Roads - Data Processing Module

## Description

This module contains the scripts to process the data incoming from the ATCLL SLP and the external aplications HERE and OpenWeather. Also contains a trained model to detect potholes.

## Contents

- `main.py` - Starts all the other scripts.

- `mqtt.py` - Connects the the broker with the ATCLL SLP data and receives and sends messages throw the broker.

- `process_service.py` -  Receives the data from the ATCLL SLP and processes it to create traffic flows and also creates events if a car is driving in the wrong way.

- `here_api_service.py` - Connects to the API from HERE to fetch traffic flows and events from the platform.

- `pothole_service.py` - Receives images that come from the cameras of the ATCLL SLP and with a model trained to check for potholes checks this images.

- `utils.py` - Auxiliary functions from `pothole_service.py` 

- `scheduler.py` - Schedules the calls to the HERE API and check of image for the `pothole_service.py` 

## Installation

- Run `pip3 install virtualenv` to install the module `virtualenv`.
- Run `virtualenv venv` in root to create a virtual environment.
- Run `source venv/bin/activate` in root to enter the virtual environment.
- Run `pip3 install -r requirements.txt` to install all dependencies.

## Environment Variables

In some scripts some environment variables to be set. It is recommended to add an `.env` file in the same directory as the script contaning the required variables. 

- `here_api_service.py`, `pothole_service.py`, and `process_service.py`. 
  
  - ATCLL_BROKER_HOST - Host address
  
  - ATCLL_BROKER_PORT - Port Number
  
  - ATCLL_P33_RTSP_URL - Url of camera
  
  - HERE_API_KEY - Key of HERE
  
  - HERE_INCIDENT_URL - Url for events from HERE
  
  - HERE_FLOW_URL - Url for traffic flow from HERE
  
  - HERE_REV_GEOCODE_URL - Url for geocoding from HERE

## Authors

- Diogo Paiva, 103183

- João Fonseca, 103154

- Pedro Rasinhas, 103541

- Gonçalo Silva, 103668


