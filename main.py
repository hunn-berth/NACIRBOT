from flask import Flask, request, session
from flask_session import Session
from CommandEnum import Command 
from Nacir import Nacir

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def hello():
    return 'Hello from the default route!'
    

@app.route('/webhook', methods = ['POST', 'GET', 'PUT'])
def webhook():
        request_data = request.json
        message_id = request_data['data']['id']
        person_id = request_data['data']['personId']
        nacir = Nacir(receiver_id = person_id)
        message = None
        file_list = None
        
        if not session.get('person_id'):
          session['person_id'] = person_id
          nacir.get_person_name()
          session['person_name'] = nacir.receiver_name
          message = nacir.retrieve_message(message_id=message_id)
     
        else: 
             nacir.receiver_id = session['person_id']
             nacir.receiver_name = session['person_name']
             message = nacir.retrieve_message(message_id=message_id)
     
        if 'files' in request_data['data']:
             file_list = request_data['data']['files']
             
          
     
        match message: 
             case('help'):
                  nacir.send_command_card()
             case('devstats'):
                  if file_list:
                    nacir.send_devstats(file_list[0])
                  else:
                    nacir.send_file_not_attached_message() 
             case('memgraph'):
                  pass
        
             case _:
                  nacir.send_command_not_understood_message()
                          
        return {}


if __name__ == '__main__': 
    app.run()