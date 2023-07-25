from webexteamssdk import WebexTeamsAPI 
import os
import requests

class BotRequestHandler():

    def __init__(self) -> None:
        self.API_KEY = 'NTc2MzA2NTgtOGJjMC00ZTE0LWFiZDgtZDhhZjY5ZDYxYTFmOGMxNmM2OWUtOTZh_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'
        self.api = WebexTeamsAPI(access_token = self.API_KEY)
       
    

    def send_message(self, receiver_id, text) -> None:
        self.api.messages.create(toPersonId = receiver_id, text = text)

    
    def get_message(self, message_id) -> str:
        return self.api.messages.get(messageId= message_id).text

    def send_card(self, receiver_id, card_data) -> None:
        attachments = [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card_data
        }]
        self.api.messages.create(toPersonId = receiver_id, attachments= attachments, text='')

    def get_receiver_name_by_id(self, receiver_id) -> str:
        person = self.api.people.get(receiver_id)
        return person.firstName

    def retrieve_file(self, file_url) -> str:
        headers = {"Authorization": f"Bearer {self.API_KEY}", "Accept": "text/csv"}
        response = requests.get(url = file_url, headers = headers)
        if response.status_code == 200:
            csv_file_content = response.content.decode('utf-8')
            return csv_file_content
        else:
            print(f'Failed to retrieve file. Error code: {response.status_code}')
            return ""

    
