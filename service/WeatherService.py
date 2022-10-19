from datetime import datetime, timedelta
import requests

class WeatherService:
    def __init__(self, env):
        self.ENV = env
        self.__BS_LON = self.ENV["BRIGHTSKY_LON"]
        self.__BS_LAT = self.ENV["BRIGHTSKY_LAT"]
        self.__BS_UNIT = self.ENV["BRIGHTSKY_UNIT"]
        self.__BS_TIMEZONE = self.ENV["BRIGHTSKY_TIMEZONE"]
        self.__BS_SOURCE = self.ENV["BRIGHTSKY_SOURCE"]
        self.__endpoint = self.ENV["BRIGHTSKY_ENDPOINT"]
        self.__data_cache = {}
        self.date_current = datetime.now()
        self.data_tomorrow = datetime.now() + timedelta(days=1)

    def __set_data_cache(self, data):
        self.__data_cache = data

    def get_data_cache(self):
        return self.__data_cache

    def get_current_weather(self):
        self.update_data()
        temperature_threshold = self.get_temperature_thresholds()
        current_weather = self.get_current_weather_data()

        return {"temperature_thresholds": temperature_threshold, "current_weather": current_weather, "current_time": datetime.now().isoformat()}

    def update_data(self, start_date=None, end_date=None):
        response = self.request_data(start_date, end_date)
        json_response = response.json()

        self.__set_data_cache(json_response)

    def request_data(self, start_date=None, end_date=None):
        start_date = self.date_current.strftime("%Y-%m-%d") if start_date == None else start_date
        end_date = self.data_tomorrow.strftime("%Y-%m-%d") if end_date == None else end_date
        request_url = self.__BS_SOURCE + self.__endpoint.format(self.__BS_LAT, self.__BS_LON, self.__BS_UNIT, self.__BS_TIMEZONE, start_date, end_date)

        return requests.get(request_url)

    def get_temperature_thresholds(self):
        min_temperature = None
        max_temperature = None

        try:
            for n in self.__data_cache["weather"]:
                if max_temperature == None:
                    min_temperature = n["temperature"]
                    max_temperature = n["temperature"]
                elif n["temperature"] > max_temperature:
                    max_temperature = n["temperature"]
                elif n["temperature"] < min_temperature:
                    min_temperature = n["temperature"]
        except Exception as e:
            print(f"No valid data found while fetching temperature thresholds --- {e}")

        return {"min_temperature": min_temperature, "max_temperature": max_temperature}

    def get_current_weather_data(self, data=None):
        weather_data = self.get_data_cache() if data == None else data
        current_datetime_iso = datetime.now().isoformat()

        try:
            for index, n in enumerate(weather_data["weather"]):
                data_datetime_iso = datetime.fromisoformat(n["timestamp"]).isoformat()
                if(data_datetime_iso > current_datetime_iso):
                    return weather_data["weather"][index-1]
        except Exception as e:
            print(f"No valid data found while fetching current weather data --- {e}")

        return {}

    data_cache = property(get_data_cache)
    weather_data = property(get_current_weather_data)