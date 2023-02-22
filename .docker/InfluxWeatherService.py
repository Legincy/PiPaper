#!/usr/bin/env python3
import os
import traceback
from datetime import datetime

import pytz
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxWeatherService:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('INFLUXDB_HOST')
        self.port = os.getenv('INFLUXDB_PORT')
        self.user = os.getenv('INFLUXDB_USER')
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.org = os.getenv('INFLUXDB_ORG')
        self.password = os.getenv('INFLUXDB_PASSWORD')
        self.database = os.getenv('INFLUXDB_DATABASE')
        self.measurement = os.getenv('INFLUXDB_MEASUREMENT')
        self.weather_api = os.getenv('WEATHER_API')
        self.position_lon = os.getenv('LON')
        self.position_lat = os.getenv('LAT')
        self.start_date = datetime.fromisoformat(os.getenv('START_DATE')).replace(tzinfo=pytz.UTC)
        self.now = datetime.now(pytz.UTC)

        host_combined = f"http://{self.host}:{self.port}"
        self.client = InfluxDBClient(url=host_combined, token=self.token, org=self.org)


    def main(self):
        if self.client.ping() is not True:
            raise Exception("Connection to InfluxDB failed")

        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        date_cursor = self.start_date

        last_timestamp = self.get_last_point()
        if last_timestamp is not None:
                date_cursor = last_timestamp

        while date_cursor < self.now:
            date_breakpoint = date_cursor + relativedelta(months=6)
            if date_breakpoint > self.now:
                date_breakpoint = self.now


            date_cursor_str = date_cursor.isoformat()
            date_breakpoint_str = date_breakpoint.isoformat()

            request_url = f"{self.weather_api}/weather?lat={self.position_lat}&lon={self.position_lon}&date={date_cursor_str}&last_date={date_breakpoint_str}"
            print(request_url)


            request = requests.get(request_url)
            print(request)
            response_json = request.json()
            date_cursor = date_breakpoint

            data_list = []

            try:
                for entry in response_json["weather"]:
                    print(entry["timestamp"])
                    data = {"measurement": self.measurement, "tags": {}, "fields": {}, "time": entry["timestamp"]}

                    for key in entry:
                        value =  entry[key]

                        if value is None:
                            continue
                        if type(value) is str or type(value) is int or type(value) is float:
                            data["fields"][key] = value
                        else:
                            data["fields"][key] = str(value)

                    data_list.append(data)

                write_api.write(self.database, self.org, data_list)
                write_api.flush()
            except Exception :
                print(traceback.format_exc())

        write_api.close()

    def get_last_point(self):
        query_api = self.client.query_api()
        query = f'from(bucket: "{self.database}")' \
                '|> range(start: 0, stop: now())' \
                f'|> filter(fn: (r) => r["_measurement"] == "{self.measurement}")' \
                '|> keep(columns: ["_time"])' \
                '|> last(column: "_time")' \

        result = query_api.query(query)

        if len(result) == 0:
            return None

        return result[0].records[0]["_time"]

if __name__ == '__main__':
    ws = InfluxWeatherService()
    ws.main()