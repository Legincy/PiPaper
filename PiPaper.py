#!/usr/bin/python
# -*- coding:utf-8 -*-

import locale
import logging as log
import os
import time
from datetime import datetime
import schedule
from dotenv import dotenv_values
from PIL import Image, ImageDraw, ImageFont
from lib.epd2in7 import EPD
from service.GoogleCalenderService import GoogleCalendarService
from service.WeatherService import WeatherService
from ComponentController import ComponentController

static_dir = os.path.join(os.path.dirname(__file__), "static")
font_dir = os.path.join(static_dir, "fonts")
icon_dir = os.path.join(static_dir, "icons")

class PiPaper:
    def __init__(self):
        self.ENV = dotenv_values("./config/.env")
        self.__APP_LOCALE = self.ENV["APP_LOCALE"]
        self.__LOG_FILE = self.ENV["LOG_FILE"]
        self.__LOG_LEVEL = self.ENV["LOG_LEVEL"]
        self.__epd = EPD()
        self.weather_service = WeatherService(self.ENV)
        self.calendar_service = GoogleCalendarService(self.ENV)
        self.component_controller = ComponentController({"width": self.__epd.width, "height": self.__epd.height}, icon_dir, font_dir)

        log.basicConfig(level=log.INFO, format='[%(asctime)s] --- [%(levelname)s]:  %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        locale.setlocale(locale.LC_TIME, self.__APP_LOCALE)

        self.init_display()


    def update_display(self):
        self.render_home_screen()

    def render_home_screen(self):
        surface = Image.new('1', (self.__epd.height, self.__epd.width), 255)
        cursor = ImageDraw.Draw(surface)
        weather_data = self.weather_service.get_prepared_weather_data()
        calendar_data = self.calendar_service.get_data_cache()

        date_component = self.component_controller.draw_current_datetime(surface, 0)
        weather_component = self.component_controller.draw_weather_tile(weather_data, surface, date_component["height"])
        calendar_component = self.component_controller.draw_calendar_schedules(calendar_data, surface, weather_component["height"])

        self.__epd.display(self.__epd.getbuffer(surface))

    def init_display(self):
        self.__epd.init()
        self.__epd.Clear(0xFF)
        self.update_display()

    def main(self):
        schedule.every().minute.at(':00').do(self.update_display)
        schedule.every().hour.do(self.weather_service.update)
        schedule.every(1).minutes.do(self.calendar_service.update)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    instance = PiPaper()
    instance.main()
