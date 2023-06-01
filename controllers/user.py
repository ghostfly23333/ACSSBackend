from flask import Blueprint

user = Blueprint("user", __name__)

@user.route("/alter/mode")
def alter_mode():
    raise NotImplementedError

# TODO: Add more routes here
