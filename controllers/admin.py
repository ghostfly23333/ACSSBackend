from flask import Blueprint

admin = Blueprint("admin", __name__)

@admin.route("/query/state")
def query_state():
    raise NotImplementedError

# TODO: Add more routes here
