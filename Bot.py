import os
import webexteamssdk as wts
import requests
import pandas as pd
import io
import task_func as tf
import json
from io import StringIO

class BotRequestHandler():
    def __init__(self):
        self.token = "YTRmYWNlNzMtNDYwMy00MGMyLTllMjMtNDM2OTJlYjk4YTY5OWQ3ZWM5NGYtZTNl_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
        self.api = wts.WebexTeamsAPI(access_token=self.token)

    def sendMessage(self, personID, text) -> None:
        self.api.messages.create(toPersonId=personID, text=text)
    
    def retrieveFile(self, fileURL) -> pd.DataFrame:
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url=fileURL, headers=headers)
        if response.status_code == 200:
            response_cvs = response.text
            csvStringIO = StringIO(response_cvs)
            df = pd.read_csv(csvStringIO, sep=",")
            return df
        else:
            print(f"Failed to retive file. Error code: {response.status_code}")
            
        
    
    def getMessage(self, messageID) -> str:
        messageObject = self.api.messages.get(messageId=messageID)
        #print("Message Text" + messageObject.text)
        return messageObject.text
    
class Bot():
    def __init__(self, data, handler : BotRequestHandler):
        self.personId = "Y2lzY29zcGFyazovL3VzL1dFQkhPT0svMWY4YzkyMzAtZTJiNy00Zjg3LWIwMmUtNDA1NmU3NDg0MTY1"
        self.event = data["event"]
        self.sender = data["data"]["personId"]
        self.roomID = data["data"]["roomId"]
        if "files" in data["data"]:
            self.files = data["data"]["files"]
        self.handler = handler
        self.messageID = data["data"]["id"]
        self.commands = ["help", "about", "csv"]

    def showCommands(self):
        if self.personId != self.sender:
            message =  "Hi, I am NACIRBOT and I will help you to analyze your network devices. Next, you will find the commands available."
            for c in self.commands:
                message += "\n-{}".format(c)
            self.handler.sendMessage(personID=self.sender, text= message)
    
    def getCommand(self):
        words = list(self.handler.getMessage(self.messageID).split(" "))
        if words[0] in self.commands:
            print("Executed command:" + words[0])
            self.run_tasks()
        else:
            self.showCommands()
    
    def run_tasks(self):
        if self.files != None:
            df =  self.handler.retrieveFile(self.files[0])
            df = tf.format_cvs(df)
            df= tf.testReachability(df)
            df=tf.checkNetconf(df)
            #df = tf.retriveWithRestconf(df)
            print(df)
            
