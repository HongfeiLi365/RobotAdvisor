from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def hello():   
    if request.method =='GET':
        return 'Hello From Flask!\nWelcome to Robot Advisor!'

if __name__ == '__main__':
    app.run()