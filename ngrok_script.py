import requests
from requests.auth import HTTPBasicAuth
import json
 

# Cisco API credentials
webhookId = 'Y2lzY29zcGFyazovL3VzL1dFQkhPT0svMWY4YzkyMzAtZTJiNy00Zjg3LWIwMmUtNDA1NmU3NDg0MTY1'
API_URL = f'https://webexapis.com/v1/webhooks/{webhookId}'
API_KEY = ''


URL_NGROK = 'https://3d1e-187-169-224-134.ngrok-free.app'+'/webhook'


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
