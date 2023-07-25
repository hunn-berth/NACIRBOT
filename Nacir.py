from BotRequestHandler import BotRequestHandler
import json
from io import StringIO
import pandas as pd
import task_func as tf
import time 

class Nacir():

    """Representation of the Network Automatic Configuration and Information Retrieval (NACIR) bot """

    def __init__(self, receiver_id) -> None:

        self.request_handler = BotRequestHandler()
        self.receiver_id = receiver_id

    def get_person_name(self) -> None:
        self.receiver_name = self.request_handler.get_receiver_name_by_id(self.receiver_id)

    def send_command_not_understood_message(self) -> None:
        #If the name of the receiver name has been obtained, make the message more personal by using his name
        try:
            self.request_handler.send_message(receiver_id=self.receiver_id, text= f'I am sorry, {self.receiver_name}. I did not understand your command, please type help for a list of available commands!')
        #If for some strange, unforeseen reason this method is called without Nacir having an attribute called receiver_name 
        except: 
            self.request_handler.send_message(receiver_id=self.receiver_id, text= f'I am sorry.  I did not understand your command, please type help for a list of available commands!')

    def send_file_not_attached_message(self):
            self.request_handler.send_message(receiver_id= self.receiver_id, text = f'You forgot to attach a file, I require a file to execute this command. Please attach one, {self.receiver_name}.')



    def retrieve_message(self, message_id) -> str: 
        message = ""
        try: 
            message = self.request_handler.get_message(message_id).lower()
            return message 
        except:
            #self.request_handler.send_message(self.receiver_id, text="You forgot to add text to the message, please type one of my commands, provide attachments if needed and then hit enter.")
            return message
    
    


    def customize_card(self, card_data) -> str: 
        split_greeting = card_data['body'][2]['text'].split(" ")
        split_greeting.insert(1, f'{self.receiver_name}.')
        new_first_word = split_greeting[0] + ','
        split_greeting[0] =new_first_word
        customized_greeting = ' '.join(split_greeting)
        card_data['body'][2]['text'] = customized_greeting
        return card_data
      
    

    def send_command_card(self):
        with open('./cards/commandCard.json') as command_card_file: 
            card_data = json.load(command_card_file)

        customized_card_data = self.customize_card(card_data)

        self.request_handler.send_card(receiver_id= self.receiver_id, card_data = customized_card_data)


    def send_devstats(self, file_url: str ):
        #CHECK THIS !!!!
        file_content = self.request_handler.retrieve_file(file_url=file_url)
        csvStringIO = StringIO(file_content)
        try:
            df = pd.read_csv(csvStringIO, sep=',')
        except:
            self.request_handler.send_message(self.receiver_id, f'I was expecting a .csv file, {self.receiver_name}. Please rerun the command with a .csv file attached.')
            return ''
        df = tf.format_csv(df)
        processed_df = self.processData(df)
        self.processCards(processed_df)
        return df 
      
        

    def processData(self, df_to_process):

        df = tf.testReachability(df_to_process)
        df=tf.checkNetconf(df)
        df = tf.retriveWithRestconf(df)
        df = tf.get_potentialBugs(df)
        df = tf.get_PSIRT(df)
        return df
        
    
    def processCards(self, df):
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
                with open('./cards/card_no.json') as file:
                    json_data = json.load(file)
                json_data['body'][1]['columns'][1]['items'][1]['text'] = row['Reachability']
                json_data['body'][1]['columns'][1]['items'][0]['text'] = row['IP address']
            #Load json card template and send it to the user
        
            self.request_handler.send_card(self.receiver_id, json_data)
            time.sleep(2)


    def send_memory_graph(self):
        pass


    

