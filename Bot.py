import os
import webexteamssdk as wts

class BotRequestHandler():
    def __init__(self):
        self.token = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        self.api = wts.WebexTeamsAPI(access_token=self.token)

    def welcomeMessage(self, personID):
        self.api.messages.create(toPersonId=personID, text="Hola Mundo!")