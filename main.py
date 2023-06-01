from flask import Flask
from controllers.admin import admin
from controllers.user import user

app = Flask(__name__)

@app.route("/")
def version_info():
    return {
        "version": "1.0.0",
    }

@app.route("/register")
def register():
    raise NotImplementedError

@app.route("/login")
def login():
    raise NotImplementedError

app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(user, url_prefix="/user")

print(app.url_map)
