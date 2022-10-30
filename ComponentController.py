#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class ComponentController:
    def __init__(self, resolution, icon_dir, font_dir):
        self._icon_dir = icon_dir
        self._font_dir = font_dir
        self._weather_icons = self.load_icons(target="weather")
        self._resolution_dict = resolution;
        self._gap = 5
        self._padding_side = 2
        self._text_gap = -3

    def draw_weather_tile(self, data, surface, pos_y):
        component_cursor = pos_y + self._gap
        tmp_weather_component_height = 0
        cursor = ImageDraw.Draw(surface)
        weather_slots = 4
        slot_width = self._resolution_dict["height"] / weather_slots

        for i in range(0, 4):
            weather_icon = self._weather_icons[data["weather_today"][i]["icon"]]
            slot_middle = (slot_width * (i+1)) - slot_width/2
            icon_position_middle = int(slot_middle - weather_icon.width/2)

            font = ImageFont.truetype(f'{self._font_dir}/Montserrat-Bold.ttf', 11)
            txt_time = self.build_content_dict(font, datetime.fromisoformat(data["weather_today"][i]["timestamp"]).strftime("%H:%M"))
            tmp_weather_component_height += txt_time["height"]

            surface.paste(weather_icon, (icon_position_middle, component_cursor+txt_time["height"]))
            cursor.text((slot_middle-txt_time["width"]/2, component_cursor), txt_time["text"], font=font, fill=0x00)
            tmp_weather_component_height += weather_icon.height

            font = ImageFont.truetype(f'{self._font_dir}/Montserrat-SemiBold.ttf', 10)
            txt_temperature = self.build_content_dict(font, f'{data["weather_today"][i]["temperature"]}°C')
            cursor.text((slot_middle-txt_temperature["width"]/2, component_cursor+txt_time["height"]+weather_icon.height), txt_temperature["text"], font=font, fill=0x00)
            tmp_weather_component_height += txt_temperature["height"]

        return {"height" : component_cursor+int(tmp_weather_component_height/weather_slots), "width": self._resolution_dict["width"]}

    def draw_current_datetime(self, surface, pos_y):
        component_cursor = pos_y + self._gap
        current_timestamp = datetime.now()
        cursor = ImageDraw.Draw(surface)

        font = ImageFont.truetype(f'{self._font_dir}/Montserrat-Bold.ttf', 12)
        txt_time = self.build_content_dict(font, current_timestamp.strftime("%H:%M"))
        cursor.text((self._resolution_dict["height"]-txt_time["width"]-self._padding_side, component_cursor), txt_time["text"], font=font, fill=0x00)

        txt_date = self.build_content_dict(font, current_timestamp.strftime("%d. %B %Y"))
        cursor.text((self._padding_side, component_cursor), txt_date["text"], font=font, fill=0x00)
        component_cursor += txt_date["height"]

        font = ImageFont.truetype(f'{self._font_dir}/Montserrat-Medium.ttf', 12)
        txt_day = self.build_content_dict(font, current_timestamp.strftime("%A"))
        cursor.text((self._padding_side, component_cursor), txt_day["text"], font=font, fill=0x00)
        component_cursor += txt_day["height"]

        return {"height" : component_cursor, "width": self._resolution_dict["width"]}

    def draw_calendar_schedules(self, data, surface, pos_y):
        component_cursor = pos_y + self._gap
        init_component_cursor = component_cursor
        cursor = ImageDraw.Draw(surface)
        item_gap = 5
        schedule_height = 0

        for index, event in enumerate(data):
            font = ImageFont.truetype(f'{self._font_dir}/Montserrat-Medium.ttf', 10)
            txt_start_time = self.build_content_dict(font, f'[{datetime.fromisoformat(event["start"]["dateTime"]).strftime("%H:%M")}]')
            cursor.text((self._padding_side, component_cursor), txt_start_time["text"], font=font, fill=0x00)

            txt_end_time = self.build_content_dict(font, f'[{datetime.fromisoformat(event["end"]["dateTime"]).strftime("%H:%M")}]')
            cursor.text((self._resolution_dict["height"]-txt_end_time["width"]-self._padding_side, component_cursor), txt_end_time["text"], font=font, fill=0x00)

            time_width = txt_start_time["width"] + txt_end_time["width"]
            font = ImageFont.truetype(f'{self._font_dir}/Montserrat-SemiBold.ttf', 11)
            txt_summary = self.build_content_dict(font, event["summary"], self._resolution_dict["height"]-time_width)
            cursor.text((self._resolution_dict["height"]/2-txt_summary["width"]/2, component_cursor), txt_summary["text"], font=font, fill=0x00)
            component_cursor += txt_summary["height"]

            font = ImageFont.truetype(f'{self._font_dir}/Montserrat-Medium.ttf', 10)
            event_description = "" if "description" not in event else event["description"]
            txt_description = self.build_content_dict(font, event_description)
            cursor.text((self._padding_side, component_cursor), txt_description["text"], font=font, fill=0x00)
            component_cursor += txt_description["height"] + item_gap

            if((component_cursor-init_component_cursor)/(index+1)+component_cursor > self._resolution_dict["width"]):
                break

        return {"height" : component_cursor, "width": self._resolution_dict["width"]}

    def build_content_dict(self, font, content_dict="", content_width=None):
        content_width = self._resolution_dict["height"] if content_width == None else content_width
        tmp_surface = Image.new('1', (self._resolution_dict["height"], self._resolution_dict["width"]), 255)
        cursor = ImageDraw.Draw(tmp_surface)

        ascent, descent = font.getmetrics()
        (width, baseline), (offset_x, offset_y) = font.font.getsize(content_dict)
        content_dict_height = ascent+descent
        content_dict_width = cursor.textlength(content_dict, font)

        is_overflowing = content_dict_width > content_width-self._padding_side*2
        if(is_overflowing):
            while(is_overflowing):
                content_dict = content_dict.rsplit(' ', 1)[0]
                is_overflowing = cursor.textlength(content_dict, font) > content_width
            content_dict = content_dict[:-3] + "..."
            content_dict_width = cursor.textlength(content_dict, font)


        content_dict_width_int = int(content_dict_width)
        content_dict_height_int = int(content_dict_height)+self._text_gap

        return {"height": content_dict_height_int, "width": content_dict_width_int, "text": content_dict }

    def load_icons(self, target, icon_dir=None):
        icon_dir = self._icon_dir if icon_dir == None else icon_dir
        target_dir = os.path.join(icon_dir, target)
        result = {}

        for file_name in os.listdir(target_dir):
            dir_obj = os.path.join(target_dir, file_name)

            if os.path.isfile(dir_obj):
                splitted_file_name = file_name.split(".")[0]
                img = Image.open(open(dir_obj, 'rb'))
                result[splitted_file_name] = img.resize((int(img.width * 0.5), int(img.height * 0.5)))

        return result