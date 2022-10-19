import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import datetime

class GoogleCalendarService:
    def __init__(self, env):
        self.ENV = env
        self.__GOOGLE_API_SOURCE = self.ENV["GOOGLE_API_SOURCE"]
        self.__EXTRACTED_SCOPES = self.ENV["GOOGLE_API_SCOPES"].split(",")
        self.__GOOGLE_API_SCOPES =  [self.__GOOGLE_API_SOURCE + scope for scope in self.__EXTRACTED_SCOPES ]
        self.__APP_CONFIG_PATH = self.ENV["APP_CONFIG_PATH"]
        self.__user_credentials = None

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

    def main(self):
        self.init_user_credentials()

        try:
            service = build('calendar', 'v3', credentials=self.__user_credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z'

            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event)

        except HttpError as error:
            print('An error occurred: %s' % error)
