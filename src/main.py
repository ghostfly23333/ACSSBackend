from flask import Flask
from controller import app as controller

app = Flask(__name__)
app.register_blueprint(controller)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=10443,debug=True)