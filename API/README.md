# ATCLL - Safe Roads - API Module

## Description

This module contains the necessary files for the API. The API was developed in FastAPI and is hosted at [https://api.atcll-data-dev.nap.av.it.pt](https://api.atcll-data-dev.nap.av.it.pt)

## Endpoints

/events - Get all events

/events?={filter1}=value&{filter2}=value - Get Filtered events

/flows - Get all flows

/flows?={filter1}=value&{filter2}=value - Get Filtered flows

/graphs - Get all graphs

/graphs?={filter1}=value&{filter2}=value - Get Filtered graphs

/docs - Swagger Documentation

#### Filters

- type (str) - Events and Graphs
  
  - accident
  
  - road_work
  
  - congestion
  
  - road_hazard
  
  - immobilized_vehicle
  
  - closed_road
  
  - police_presence
  
  - flood
  
  - pothole
  
  - wrong_way

- source (str) - Events and Graphs
  
  - atcll 
  
  - here

- location (str) - Events and Graphs

- start (str) - All
  
  - Format = '%Y-%m-%dT%H:%M:%S%z'

- end (str) - All
  
  - Format = '%Y-%m-%dT%H:%M:%S%z'

- weather (str) - Graphs
  
  - temperature
  
  - humidity
  
  - temperature,humidity

## Installation

- Run `pip3 install virtualenv` to install the module `virtualenv`.
- Run `virtualenv venv` in root to create a virtual environment.
- Run `source venv/bin/activate` in root to enter the virtual environment.
- Run `pip3 install -r requirements.txt` to install all dependencies.

## Environment Variables

In some scripts some environment variables to be set. It is recommended to add an `.env` file in the same directory as the script contaning the required variables.

- ATCLL_BROKER_HOST - Host address

- ATCLL_BROKER_PORT - Port Number

- MONGO_DATABASE - Name of Mongo Database

- MONGO_ROOT_USERNAME - Username of Mongo

- MONGO_ROOT_PASSWORD - Password of Mongo

- MONGO_HOST - Host address of Mongo

- MONGO_PORT - Port Number Of Mongo

- DATABASE_URL - URL of Mongo Database

- JWT_ALGORITHM - Algorithm of JSON Web Token

- JWT_PRIVATE_KEY - Private Key of JSON Web Token

- JWT_PUBLIC_KEY - Public Key of JSON Web Token

- ACCESS_TOKEN_EXPIRES_IN - Expiration of Access Token

- REFRESH_TOKEN_EXPIRES_IN - Expiration of Refresh Token

- CLIENT_ORIGIN - CORS URL

- OPENWEATHER_API_KEY - Key to access OpenWeather API

- OPENWEATHER_HISTORY_URL - Url to access history data from OpenWeather

## Authors

- Diogo Paiva, 103183

- João Fonseca, 103154


