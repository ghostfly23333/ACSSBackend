
from flask import Blueprint
app = Blueprint('default_controller',__name__)


@app.route('/')
def index():
    return '/'



@app.route('/register', methods=['POST'])
def register():
    """
    @api {post} /register 用户注册
    @apiName Register
    @apiGroup Default
    @apiBody {String} username 用户名
    @apiBody {String} password 密码
    @apiSuccess {json} Success-Response
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "注册成功"
      }
    @apiError {json} Error-Response
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "用户名已存在"
      }
    """
    return 'register'


@app.route('/login', methods=['POST'])
def login():
    """
    @api {post} /login 用户登录
    @apiName Login
    @apiGroup Default
    @apiBody {Int} auth 权限[0:普通用户, 1:管理员]
    @apiBody {String} username 用户名
    @apiBody {String} password 密码
    @apiSuccess {String} token 用户token 
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "登录成功",
        "token": "TOKEN"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 401 UNAUTHORIZED
      {
        "status": 1,
        "message": "用户名或密码错误"
      }
    """
    return 'login'
