from flask import Blueprint
app = Blueprint('user_controller',__name__)

@app.route('/charge',methods=['POST'])
def charge():
    """
    @api {post} /user/charge 充电请求
    @apiName Charge
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} username 用户名
    @apiParam {String} car_id 车辆id
    @apiParam {Int} mode 充电模式(0:常规, 1:快速)
    @apiParam {Double} amount 电量
    @apiSuccess {String} bill_id 账单id
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "充电成功",
        "data": {
          "bill_id": ""
        }
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "请求失败"
      }
    """
    return 'user/charge'

@app.route('/query/profile', methods=['GET'])
def query_profile():
    """
    @api {get} /user/query/profile 获取用户信息
    @apiName QeuryProfile
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiSuccess {String} username 用户名
    @apiSuccess {json[]} bill 账单 
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "获取成功",
        "data": {
          "username": "admin",
          "bill": [
            {
              "id": "",
              "date": "",
              "cost": 0,
            }
          ]
        }
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 401 UNAUTHORIZED
      {
        "status": 1,
        "message": "token已过期"
      }
    """
    return 'user/query/profile'


@app.route('/query/bill', methods=['GET'])
def query_bill():
    """
    @api {get} /user/query/bill 查询账单
    @apiName QueryBill
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} bill_id 账单id
    @apiSuccess {String} bill_id 账单id
    @apiSuccess {Int} status 账单状态 (0:已提交, 1:正在充电, 2:已完成, 3:已取消)
    @apiSuccess {String} date 账单日期
    @apiSuccess {String} car 车辆id
    @apiSuccess {Double} amount 总电量
    @apiSuccess {Double} duration 总时间
    @apiSuccess {Int} mode 充电模式(0:常规, 1:快速)
    @apiSuccess {Int} pile 充电桩id
    @apiSuccess {String} start_time 开始时间
    @apiSuccess {String} end_time 结束时间 
    @apiSuccess {Double} service 服务费
    @apiSuccess {Double} charge 充电费用
    @apiSuccess {Double} total 总费用
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": {
          "bill_id": "",
          "date": "",
          "car": "",
          "status": 0,
          "detail"{
            "amount": 0,
            "duration": 0,
            "mode": 0,
            "pile": 0,
            "start_time": "",
            "end_time": ""
          }
          "cost":{
            "service": 0,
            "charge": 0,
            "total": 0
          }
        }
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "账单不存在"
      }
    """
    return 'user/query/bill'



@app.route('/query/queue', methods=['GET'])
def query_queuing():
    """
    @api {get} /user/query/queue 查询排队信息
    @apiName QueryQueue
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} car_id 车辆id
    @apiSuccess {String} car_id 车辆id
    @apiSuccess {String} pile_id 充电桩id
    @apiSuccess {Int} wait 排队位置 
    @apiSuccess {Int} section 区域(0:等待区, 1:充电区)
    @apiSuccess {Int} status 状态(0:等待中, 1:充电中)
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": {
          "car_id": "",
          "pile_id": "",
          "wait": 0,
          "section": 0,
          "status": 0
        }
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "车辆不存在"
      }
    """
    return 'user/query/queue'



@app.route('/alter/amount', methods=['POST'])
def alter_amount():
    """
    @api {post} /user/alter/amount 修改电量
    @apiName AlterAmount
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} bill_id 账单id
    @apiParam {Double} amount 电量
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "修改成功"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "账单不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许修改"
      }
    """
    return 'user/alter/amount'



@app.route('/alter/mode', methods=['POST'])
def alter_mode():
    """
    @api {post} /user/alter/mode 修改充电模式
    @apiName AlterMode
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} bill_id 账单id
    @apiParam {Int} mode 充电模式(0:常规, 1:快速)
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "修改成功"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "账单不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许修改"
      }
    """
    return 'user/alter/mode'



@app.route('/alter/end', methods=['POST'])
def alter_end():
    """
    @api {post} /user/alter/end 修改结束时间
    @apiName AlterEnd
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} bill_id 账单id
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "已终止"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "账单不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "终止失败"
      }
    """
    return 'user/alter/end'



@app.route('/alter/cancel', methods=['POST'])
def alter_cancel():
    """
    @api {post} /user/alter/cancel 取消账单
    @apiName AlterCancel
    @apiGroup User
    @apiHeader {String} token 用户token
    @apiParam {String} bill_id 账单id
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "已取消"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "账单不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许取消"
      }
    """
    return 'user/alter/cancel'