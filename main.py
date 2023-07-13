import flask
from Bot import BotRequestHandler, Bot

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

#The endpoint that will receive POST from WebexAPI
@app.route('/webhook', methods=['POST', 'GET', 'PUT'])
def webhook():
    print("RECEIVED EVENT")
    data = flask.request.json
    print(data)
    bot =  Bot(data, handler)
    bot.getCommand()
    return {}

if __name__ == '__main__':
    handler = BotRequestHandler()
    app.run()#debug=True