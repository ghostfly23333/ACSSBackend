from flask import Blueprint
from controller.user import app as user
from controller.admin import app as admin
from controller.basic import app as basic

app = Blueprint('controller',__name__)
app.register_blueprint(user,url_prefix='/user')
app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(basic)