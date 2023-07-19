import requests
from requests.auth import HTTPBasicAuth
import json
 

# Cisco API credentials
webhookId = 'Y2lzY29zcGFyazovL3VzL1dFQkhPT0svMWY4YzkyMzAtZTJiNy00Zjg3LWIwMmUtNDA1NmU3NDg0MTY1'
API_URL = f'https://webexapis.com/v1/webhooks/{webhookId}'
API_KEY = 'YTRmYWNlNzMtNDYwMy00MGMyLTllMjMtNDM2OTJlYjk4YTY5OWQ3ZWM5NGYtZTNl_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'


URL_NGROK = 'https://d0ac-2001-420-140e-1250-351e-5e48-cc3a-e51e.ngrok-free.app'+'/webhook'


# Set the headers with API key
headers = {
    'Authorization': 'Bearer ' + API_KEY,
    'Content-Type': 'application/json'
}
data ={
    'name': 'Webhook Bot Bugs ',
    'targetUrl': URL_NGROK,
}
# Send GET request to retrieve webhooks
response = requests.put(API_URL, headers=headers,json=data)

# Check if the request was successful
if response.status_code == 200:
    print('URL UPDATED: '+URL_NGROK)
else:
    print(f"Failed to retrieve webhooks. Error code: {response.status_code}")
