import requests #Libary for interacting with Webex API

import json  

import os 

#from webex_bot.webex_bot import WebexBot 



url = "https://webexapis.com/v1/messages" #Global variable that all functions manipulate for sending a request
botToken = "NTc2MzA2NTgtOGJjMC00ZTE0LWFiZDgtZDhhZjY5ZDYxYTFmOGMxNmM2OWUtOTZh_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f" #Add your token here, obtained from developer.webex
sender = "" #Sender email, used for testing purposes. Add your email!


def sendMessage(): 

    '''This function sends a message to a desired user specified by the toPersonEmail header''' #This is a docsting

    #Create header dictionary according to webex api
    headers = {"Authorization": f"Bearer {botToken}" , "Accept": "application/json"}

    #Building post body: personEmail is the person that will receive the message, text is the content of the message
    payload = {'toPersonEmail': 'hcarrill@cisco.com', "text" : "Hello, master. Thanks for creating me!"}
    
    #Send the request to the global url, using the defined headers, and data
    response = requests.post(url, headers = headers, data = payload)
    

    print(response.status_code) #200 = OK, 300 = File moved, 400 = User made a mistake, 500 = Server error


    responseDict = response.json() #Convert response content to json format or "dictionary"

    print(responseDict) #What does the dictionary contain? {key: value,}

    messageID = (responseDict['id']) #Use key id for retrieving the id of the message


    return messageID #Return id for testing purposes or subsquent function calls



def getMessageInfo(messageID): 

    

    """

    This function obtains the info of a particular message using its messageID (Received as parameter)

    """


    #creating headers, authorization allows us to make api calls, and accept is the response type

    headers = {"Authorization": f"Bearer {botToken}", "Accept": "application/json"}

    #The message ID should be added as a parameter in the get request

    params = {"messageID": messageID} #https://webexapis.com?messageId=123

    
    print('Sending get messages request')

    #send request with params
    response = requests.get(url, headers = headers, params= params)
    print(response.status_code)
    print(response.json())


def printMessageFile(message):

    """
        This function checks if the user attached a file to the message. If the message containes a file, the file content is displayed.
        It receives a message (that is itself dictionary) as parameter
    """

    #If the message has a file 
    if 'files' in message.keys():
    #The message itself its a dictionary so we should access its content using dictionary sintax                     
        fileUrl = message['files'][0]  #Accesing the first file of the message dictionary

        print(f"The url for the file attached to the message is: {fileUrl}. \n displaying its content....")

        headers = {"Authorization": f"Bearer {botToken}", "Accept": "application/json"}

        #The url used for this request is not the webex api url that was used before. When the user sent a message containing a file, a new url for the file was created, that's the one we are using.
        response = requests.get(fileUrl, headers=headers)



        print(response.content)

    else:
        print('The message did not contain a file')


def listDirectMessages():

    """This function lists all the direct messages that a Bot and a user have sent in one room, the room is selected by the api, according to the user email which
    is provided as a parameter"""
    
    newUrl = f'{url}/direct' #Create new url because the endpoint for getting a list of messages has a different url

    #Bot token is used for retrieving its chat rooms, then they are further filtered by the sender's email

    headers = {"Authorization": f"Bearer {botToken}", "Accept": "application/json"}

    #The direct endpoint receives a user email as parameter or a personID for identifying the room and retrieving all messages from it 
    params = {'personEmail': sender}

    #Send get request using the retrieved file ulr as parameter.
    response = requests.get(newUrl, headers= headers, params = params)

    responseDict = response.json() #Obtain response dictionary

    mostRecentMessage = responseDict['items'][0] #Retrieve the first message from the list (most recent) {'items': [1,2,3,4,5]}

    #Print the value of the text key of the most recent message
    print(mostRecentMessage['text'])

    #Helper function to check if message contains a file
    printMessageFile(mostRecentMessage) #{'id': "", 'roomId':"", 'files':"", 'text':""}


def createWebhook():

    webhookCreationUrl = "https://webexapis.com/v1/webhooks"

    headers = {"Authorization": f"Bearer {botToken}", "Accept": "application/json"}

    payload = {'name': 'NACIR_webhook', 'targetUrl': 'https://0d8e-187-208-177-240.ngrok.io/webhook', 'resource': 'messages', 'event': 'created'}

    response = requests.post(webhookCreationUrl, data=payload, headers= headers)

    print(f'Created the webhook and got f{response.content}')

def updateWebhook():

    WEBHOOK_ID = os.environ["NACIR_WEBHOOK_ID"] 
    API_KEY = os.environ["WEBEX_TEAMS_ACCESS_TOKEN"]
    API_URL = f'https://webexapis.com/v1/webhooks/{WEBHOOK_ID}'
    NGROK_URL = 'https://d35b-187-208-177-240.ngrok.io/webhook' 

    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

    payload = {'name': 'NACIR_webhook', 'targetUrl': NGROK_URL}

    response = requests.put(API_URL, headers=headers, json = payload)

    if response.status_code == 200: 
        print('URL UPDATED: ' + NGROK_URL)
    else: 
        print(f'Failed to retrieve webhooks. Error code: {response.status_code}')





def main():

    updateWebhook()

    #Note that the getMessageInfo needs a messageID parameter, it can be obtained by using the sendMessage function and storing its value on a variable

    
    #messageID = sendMessage()
    #getMessageInfo(messageID)
    #listDirectMessages()


main()



