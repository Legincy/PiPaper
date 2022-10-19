import logging as log
from dotenv import dotenv_values
from service.GoogleCalenderService import GoogleCalendarService
from service.WeatherService import WeatherService
import time

class PiPaper:
    def __init__(self):
        self.ENV = dotenv_values("./config/.env")
        self.__APP_RENDER_INTERVAL = self.ENV["APP_RENDER_INTERVAL_MS"]
        self.__LOG_FILE = self.ENV["LOG_FILE"]
        self.__LOG_LEVEL = self.ENV["LOG_LEVEL"]
        self.weather_service = WeatherService(self.ENV)
        self.calendar_service = GoogleCalendarService(self.ENV)
        log.basicConfig(level=log.INFO, format='[%(asctime)s] --- [%(levelname)s]:  %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

    def request_data_update(self):
        pass

    def update_display(self):
        pass

    def main(self):
       #self.calendar_service.main()


        while True:
            print(self.weather_service.get_current_weather())
            time.sleep(60);



if __name__ == '__main__':
    instance = PiPaper()
    instance.main()
