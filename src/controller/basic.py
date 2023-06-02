from flask import Blueprint
from flask import request
from classes.Timer import timer
from flask import jsonify
from analyzer.auth import register as auth_register
from analyzer.auth import login as auth_login

app = Blueprint('default_controller', __name__)


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
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "用户名已存在"
      }
    """
    username = request.json.get('username')
    password = request.json.get('password')
    if (auth_register(username, password)):
        return jsonify({"status": 0, "message": "注册成功"})
    return jsonify({"status": 1, "message": "用户名已存在"})


@app.route('/login', methods=['POST'])
def login():
    """
    @api {post} /login 用户登录
    @apiName Login
    @apiGroup Default
    @apiBody {Int} auth 权限(0:普通用户, 1:管理员)
    @apiBody {String} username 用户名
    @apiBody {String} password 密码
    @apiSuccess {String} token 用户token 
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "登录成功",
        "token": ""
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 401 UNAUTHORIZED
      {
        "status": 1,
        "message": "用户名或密码错误"
      }
    """
    auth = request.json.get('auth')
    username = request.json.get('username')
    password = request.json.get('password')
    if auth_login(username, password, auth):
        return jsonify({"status": 0, "message": "登录成功", "token": ""})
    return jsonify({"status": 1, "message": "用户名或密码错误"}), 401


@app.route('/time', methods=['GET'])
def get_time():
    """
    @api {get} /time 获取模拟时间
    @apiName GetTime
    @apiGroup Default
    @apiSuccess {Float} stamp 时间戳(秒)
    @apiSuccess {Int} year 年
    @apiSuccess {Int} month 月
    @apiSuccess {Int} day 日
    @apiSuccess {Int} hour 时
    @apiSuccess {Int} minute 分
    @apiSuccess {Int} second 秒
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "获取成功",
        "data": {
          "stamp": 0.0,
          "year": 0,
          "month": 0,
          "day": 0,
          "hour": 0,
          "minute": 0,
          "second": 0
        }
      }
    """
    t = timer.time()
    return jsonify({"status": 0, "message": "获取成功", "data": t.to_dict()})