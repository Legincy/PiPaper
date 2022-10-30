#!/usr/bin/python
# -*- coding:utf-8 -*-

import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

class GoogleCalendarService:
    def __init__(self, env):
        self.ENV = env
        self.__GOOGLE_API_SOURCE = self.ENV["GOOGLE_API_SOURCE"]
        self.__EXTRACTED_SCOPES = self.ENV["GOOGLE_API_SCOPES"].split(",")
        self.__GOOGLE_API_SCOPES =  [self.__GOOGLE_API_SOURCE + scope for scope in self.__EXTRACTED_SCOPES ]
        self.__APP_CONFIG_PATH = self.ENV["APP_CONFIG_PATH"]
        self.__user_credentials = None
        self.__data_cache = []

        self.init_user_credentials()
        self.update()


    def __set_data_cache(self, data):
        self.__data_cache = data

    def get_data_cache(self):
        return self.__data_cache

    def init_user_credentials(self):
        token_path = self.__APP_CONFIG_PATH + 'token.json'
        credentials_path = self.__APP_CONFIG_PATH + 'credentials.json'

        if os.path.exists(token_path):
            self.__user_credentials = Credentials.from_authorized_user_file(token_path, self.__GOOGLE_API_SCOPES)

        if not self.__user_credentials or not self.__user_credentials.valid:
            if self.__user_credentials and self.__user_credentials.expired and self.__user_credentials.refresh_token:
                self.__user_credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.__GOOGLE_API_SCOPES)
                self.__user_credentials = flow.run_local_server(port=0)

            with open(token_path, 'w') as token:
                token.write(self.__user_credentials.to_json())

    def update(self):
        try:
            service = build('calendar', 'v3', credentials=self.__user_credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            self.__set_data_cache(events_result.get('items', []))

            if not self.__data_cache:
                logging.info('No upcoming events found from Google-Calendar.')
                return

        except HttpError as error:
            logging.error(f"Error while fetching events from Google-Calendar --- {error}")

    data_cache = property(get_data_cache)