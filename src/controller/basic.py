from flask import Blueprint
from flask import request
from classes.Timer import timer
from flask import jsonify
from analyzer.auth import register as auth_register
from analyzer.auth import login as auth_login
from classes.ChargingPile import charging_piles
from classes.Schduler import waiting_area

app = Blueprint('default_controller', __name__)


@app.route('/')
def index():
    return 'ACCESSABLE'


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
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "登录成功",
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
        return jsonify({"status": 0, "message": "登录成功"})
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
          "ratio": 1,
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
    data = t.to_dict()
    data['ratio'] = timer._ratio
    return jsonify({"status": 0, "message": "获取成功", "data": data})

@app.route('/test', methods=['POST'])
def get_test():
    """
    @api {post} /test 测试接口
    @apiName GetTest
    @apiGroup Default
    @apiSuccess {String} message 测试消息
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "测试成功"
      }
    """
    print(f'******************* {timer.time().to_string()} **************************')
    res = {}
    res['time'] = timer.time().to_string()
    for key in charging_piles:
        res[key] = charging_piles[key].detail()
    print(res)    
    return jsonify({"status": 0, "message": res})

@app.route('/result', methods=['POST'])
def get_result():
    """
    @api {post} /result 获取三元组结果接口
    @apiName GetResult
    @apiGroup Default
    @apiSuccess {String} message 三元组结果消息
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "获取结果成功"
      }
    """
    print(f'******************* {timer.time().to_string()} **************************')
    res = {}
    res['time'] = timer.time().to_string()
    res['waiting_area'] = waiting_area.result()
    for key in charging_piles:
        res[key] = charging_piles[key].result()  
    print(res)
    return jsonify({"status": 0, "message": res})

