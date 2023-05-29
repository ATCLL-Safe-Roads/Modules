import requests

from datetime import datetime

from app.config import settings


class OpenWeatherApiService:

    @staticmethod
    def get_history(latitude, longitude, start, cnt):
        """
        Get historic weather data from OpenWeather History API
        :param latitude: Latitude
        :param longitude: Longitude
        :param start: Datetime
        :param cnt: Number of hours since start
        :return: JSON data
        """
        params = {
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lat': latitude,
            'lon': longitude,
            'start': int(datetime.timestamp(start)),
            'cnt': cnt
        }
        r = requests.get(url=settings.OPENWEATHER_HISTORY_URL, params=params)
        return r.json()
