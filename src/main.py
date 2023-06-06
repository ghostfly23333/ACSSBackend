from flask import Flask
from controller import app as controller
from config.sys import RUNTIME_HOST, RUNTIME_PORT,RUNTIME_DEBUG

app = Flask(__name__)
app.register_blueprint(controller)

if __name__ == '__main__':
    app.run(host=RUNTIME_HOST,port=RUNTIME_PORT,debug=RUNTIME_DEBUG)