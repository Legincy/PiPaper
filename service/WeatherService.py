#!/usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
from enum import Enum
import requests
from PIL import Image, ImageDraw, ImageFont
import logging

class WeatherService:
    def __init__(self, env):
        self.ENV = env
        self.__BS_LON = self.ENV["BRIGHTSKY_LON"]
        self.__BS_LAT = self.ENV["BRIGHTSKY_LAT"]
        self.__BS_UNIT = self.ENV["BRIGHTSKY_UNIT"]
        self.__BS_TIMEZONE = self.ENV["BRIGHTSKY_TIMEZONE"]
        self.__BS_SOURCE = self.ENV["BRIGHTSKY_SOURCE"]
        self.__endpoint = self.ENV["BRIGHTSKY_ENDPOINT"]
        self.__data_cache = []
        self.date_current = datetime.now()
        self.data_tomorrow = datetime.now() + timedelta(days=1)

        self.update()


    def __set_data_cache(self, data):
        self.__data_cache = data

    def get_data_cache(self):
        return self.__data_cache

    def update(self):
        payload = []

        for i in range(0, 4):
            v_start_date = (self.date_current + timedelta(days=i)).strftime("%Y-%m-%d")
            v_end_date = (self.data_tomorrow + timedelta(days=i)).strftime("%Y-%m-%d")

            response = self.request_data(v_start_date, v_end_date)
            json_response = response.json()
            temperature_threshold = self.get_temperature_threshold(json_response)
            json_response["temperature_threshold"] = temperature_threshold
            payload.append(json_response)

        self.__set_data_cache(payload)

    def request_data(self, start_date=None, end_date=None):
        start_date = self.date_current.strftime("%Y-%m-%d") if start_date == None else start_date
        end_date = self.data_tomorrow.strftime("%Y-%m-%d") if end_date == None else end_date
        request_url = self.__BS_SOURCE + self.__endpoint.format(self.__BS_LAT, self.__BS_LON, self.__BS_UNIT, self.__BS_TIMEZONE, start_date, end_date)

        return requests.get(request_url)

    def get_temperature_threshold(self, data=None):
        weather_data = self.get_data_cache() if data == None else data
        min_temperature = None
        max_temperature = None

        try:
            for n in data["weather"]:
                if max_temperature == None:
                    min_temperature = n["temperature"]
                    max_temperature = n["temperature"]
                elif n["temperature"] > max_temperature:
                    max_temperature = n["temperature"]
                elif n["temperature"] < min_temperature:
                    min_temperature = n["temperature"]
        except Exception as error:
            logging.error(f"No valid data found while fetching temperature threshold --- {error}")

        return {"min_temperature": min_temperature, "max_temperature": max_temperature}

    def get_prepared_weather_data(self):
        payload = {"weather_today": [], "weather_forecast": [], "current_time": datetime.now().isoformat()}
        current_hour_int = int(datetime.now().strftime("%-H"))

        for i in range(0, 4):
            selected_hour = current_hour_int + i
            payload["weather_today"].append(self.__data_cache[0]["weather"][selected_hour])

        for i in range(0, 4):
            temperature_threshold = self.get_temperature_threshold(self.__data_cache[i])
            payload["weather_forecast"].append({**temperature_threshold, "icon": self.__data_cache[i]["weather"][current_hour_int]["icon"]})

        return payload

    data_cache = property(get_data_cache)
