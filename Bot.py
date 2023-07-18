import os
import webexteamssdk as wts
import requests
import pandas as pd
import io
import task_func as tf
import json
from io import StringIO
import time

class BotRequestHandler():
    def __init__(self):
        self.token = ""
        self.api = wts.WebexTeamsAPI(access_token=self.token)

    def sendMessage(self, personID, text) -> None:
        self.api.messages.create(toPersonId=personID, text=text)
    
    def sendCard(self, personID, attachments) -> None:
        self.api.messages.create(toPersonId=personID, text='CARD',attachments=attachments)
    
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
                
    def getCommand(self):
        words = list(self.handler.getMessage(self.messageID).split(" "))
        if words[0] in self.commands:
            print("Executed command:" + words[0])
            self.run_tasks()
        else:
            self.showCommands()
    
    def run_tasks(self):
        """
        Giving a CSV procees the IP's and get all the information about each device liked to the IP
        """
        if self.files != None:
            df =  self.handler.retrieveFile(self.files[0])
            df = tf.format_cvs(df)
            df= tf.testReachability(df)
            df=tf.checkNetconf(df)
            df = tf.retriveWithRestconf(df)
            df = tf.get_potentialBugs(df)
            df = tf.get_PSIRT(df)
            self.processCards(df)
            #df.to_csv("csv_file", index = False)

    def processCards(self, df):
        """
        Send information of each device, convert it to a Card and send it throught webex
        """
        for index, row in df.iterrows():
            if row['Reachability'] == 'Reachable':
                #If reachable get IP, PID, VERSION, STATUS AND OS
                with open('card_full.json') as file:
                    json_data = json.load(file)
                json_data['body'][1]['columns'][1]['items'][0]['text'] = row['IP address']
                json_data['body'][1]['columns'][1]['items'][1]['text'] = row['PID']
                json_data['body'][1]['columns'][1]['items'][2]['text'] = row['Version']
                json_data['body'][1]['columns'][1]['items'][3]['text'] = row['Reachability']
                json_data['body'][1]['columns'][1]['items'][4]['text'] = row['OS type']
                #Formating Bugs & Hyperlink (Bugs are for IOS & IOS-XE)
                string_bugs = '-'
                if type(row['Potential_bugs']) == list:
                    for e in row['Potential_bugs']:
                        string_bugs += '['+ e + ']' + '(https://bst.cisco.com/quickview/bug/'+e+')\n-'   
                else:
                    string_bugs = '-'
                json_data['body'][3]['text'] = string_bugs[:-1]
                #Formating Advisory & Hyperlink (Advisory are for IOS-XE)
                if row['OS type'] == 'IOS-XE':
                    string_PSIRT = '-'
                    if type(row['PSIRT']) == list: 
                        for e in row['PSIRT']:
                           string_PSIRT += '['+ e + ']' + '(https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/'+e+')\n-'
                    else:
                        string_PSIRT = '-'
                    #Data of memory 
                    used_mem_percent =  (int(row['Used_proc_mem']) / int(row['Total_proc_mem']) ) * 100
                    formatted_result = "{:.2f}%".format(used_mem_percent)
                    if(used_mem_percent > 30.00):
                        json_data['body'][1]['columns'][1]['items'][6]['color'] = 'attention'
                    #Adding to card the results
                    json_data['body'][5]['text'] = string_PSIRT[:-1]
                    json_data['body'][1]['columns'][1]['items'][5]['text'] = row['Configured restconf']
                    json_data['body'][1]['columns'][1]['items'][6]['text'] = formatted_result
            else:
                #if device is not reachable send template with only IP and status
                with open('card_no.json') as file:
                    json_data = json.load(file)
                json_data['body'][1]['columns'][1]['items'][1]['text'] = row['Reachability']
                json_data['body'][1]['columns'][1]['items'][0]['text'] = row['IP address']
            #Load json card template and send it to the user
            attachments= [
            {  
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": json_data
            }
            ]
            self.handler.sendCard(self.sender, attachments)
            time.sleep(2)



            

        
        
