from flask import Blueprint
from flask import request
from flask import jsonify
from analyzer.charging_request import alter_charging_mode, alter_charging_amount, cancel_charging_request
from analyzer.charging_request import submit_charging_request, query_charging_detail, query_charging_request
from analyzer.__init__ import container


app = Blueprint('user_controller',__name__)

@app.route('/charge',methods=['POST'])
def charge():
    """
    @api {post} /user/charge 充电请求
    @apiName Charge
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
    @apiParam {Int} mode 充电模式(0:常规, 1:快速)
    @apiParam {Double} amount 电量
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "请求成功",
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "请求失败"
      }
    """
    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    mode = request.json.get('mode')
    amount = request.json.get('amount')
    if (submit_charging_request(user_id, car_id, int(mode), float(amount))):
        return jsonify({
            "status": 0,
            "message": "充电成功",
        })
    else:
        return jsonify({
            "status": 1,
            "message": "重复的请求"
        })
    

@app.route('/query/request', methods=['GET'])
def query_request():
    """
    @api {get} /user/query/request 查询充电请求
    @apiName QueryRequest
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiSuccess {String} car_id 车辆id
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": ["car_id_1","card_id_2"]
      }
    """
    user_id = request.args.get('user_id')
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": query_charging_request(user_id)
    })



@app.route('/query/detail', methods=['GET'])
def query_detail():
    """
    @api {get} /user/query/detail 查询充电详情
    @apiName QueryDetail
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
    @apiSuccess {String} car_id 车辆id
    @apiSuccess {Int} mode 充电模式(0:常规, 1:快速)
    @apiSuccess {Int} status 车辆状态 (0:等待中, 1:充电中)
    @apiSuccess {String} pile_id 充电桩id
    @apiSuccess {Double} request_amount 电量
    @apiSuccess {Double} charged_amount 已充电量
    @apiSuccess {Double} duration 时间
    @apiSuccess {Double} remain 剩余时间
    @apiSuccess {String} start_time 开始时间
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": {
          "car_id": "",
          "mode": 0,
          "status": 0,
          "pile_id": "",
          "request_amount": 0,
          "charged_amount": 0,
          "duration": 0,
          "remain": 0,
          "start_time": "",
        }
      }
    """
    user_id = request.args.get('user_id')
    car_id = request.args.get('car_id')
    info = query_charging_detail(car_id)
    if info is not None:
        return jsonify({
            "status": 0,
            "message": "查询成功",
            "data": info
        })
    else:
        return jsonify({
            "status": 1,
            "message": "车辆不存在"
        })


@app.route('/query/profile', methods=['GET'])
def query_profile():
    """
    @api {get} /user/query/profile 获取用户信息
    @apiName QeuryProfile
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiSuccess {String} user_id 用户id
    @apiSuccess {json[]} bill 账单 
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "获取成功",
        "data": {
          "user_id": "",
          "bill": [
            {
              "id": "",
              "date": "",
              "car": "",
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
    user_id = request.args.get('user_id')
    bills = container.find_user(str(user_id))
    data = []
    if bills is not None:
      for bill in bills:
          data.append({
              "id": bills[bill]['bill_id'],
              "date": bills[bill]['date'],
              "car": bills[bill]['car'],
              "cost": bills[bill]['total']
          })
      return jsonify({
          "status": 0,
          "message": "获取成功",
          "data": {
              "user_id": user_id,
              "bill": data
          }
      })
    else:
      return jsonify({
          "status": 1,
          "message": "用户不存在"
      })


@app.route('/query/bill', methods=['GET'])
def query_bill():
    """
    @api {get} /user/query/bill 查询账单
    @apiName QueryBill
    @apiGroup User
    @apiParam {String} user_id 用户id
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
    user_id = request.args.get('user_id')
    bill_id = request.args.get('bill_id')
    # if cur_bill['bill_id'] !=bill_id :
    #     return jsonify(cur_bill.content)
    # else:
    # 暂时不太清楚该怎么确认是实时还是静态，暂定都是查静态报表
    bill = container.find_user_bill(user_id,bill_id)
    if bill is None:
        return jsonify({"status":1,"message":"账单不存在"})
    else:
      return jsonify({"status":0,"message":"查询成功","data":bill.to_dict()})



@app.route('/query/queue', methods=['GET'])
def query_queuing():
    """
    @api {get} /user/query/queue 查询排队信息
    @apiName QueryQueue
    @apiGroup User
    @apiParam {String} user_id 用户id
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
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
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
        "message": "车辆不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许修改"
      }
    """
    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    amount = request.json.get('amount')
    if alter_charging_amount(car_id, amount) == 0:
        return jsonify({"status": 0, "message": "修改成功"})
    elif alter_charging_amount(car_id, amount) == 1:
        return jsonify({"status": 1, "message": "车辆不存在"})
    else:
        return jsonify({"status": 2, "message": "不允许修改"})



@app.route('/alter/mode', methods=['POST'])
def alter_mode():
    """
    @api {post} /user/alter/mode 修改充电模式
    @apiName AlterMode
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
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
        "message": "车辆不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许修改"
      }
    """
    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    mode = request.json.get('mode')
    if alter_charging_mode(car_id, mode) == 0:
        return jsonify({"status": 0, "message": "修改成功"})
    elif alter_charging_amount(car_id, mode) == 1:
        return jsonify({"status": 1, "message": "车辆不存在"})
    else:
        return jsonify({"status": 2, "message": "不允许修改"})



@app.route('/alter/mode_and_amount', methods=['POST'])
def alter_mode_and_amout():
    """
    @api {post} /user/alter/mode 修改充电模式
    @apiName AlterMode
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
    @apiParam {Int} mode 充电模式(0:常规, 1:快速)
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
        "message": "车辆不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许修改"
      }
    """
    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    mode = request.json.get('mode')
    amount = request.json.get('amount')
    is_alter_mode = alter_charging_mode(car_id, mode)
    if is_alter_mode == 0:
        is_alter_amount = alter_charging_amount(car_id, amount)
        if is_alter_amount == 0:
            return jsonify({"status": 0, "message": "修改成功"})
        elif is_alter_amount == 1:
            return jsonify({"status": 1, "message": "车辆不存在"})
        else:
            return jsonify({"status": 2, "message": "不允许修改"})
    elif is_alter_mode == 1:
        return jsonify({"status": 4, "message": "车辆不存在"})
    else:
        return jsonify({"status": 5, "message": "不允许修改"})



@app.route('/alter/cancel', methods=['POST'])
def alter_cancel():
    """
    @api {post} /user/alter/cancel 取消充电
    @apiName AlterCancel
    @apiGroup User
    @apiParam {String} user_id 用户id
    @apiParam {String} car_id 车辆id
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
        "message": "车辆不存在"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 2,
        "message": "不允许取消"
      }
    """
    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    if cancel_charging_request(car_id) == 0:
        return jsonify({"status": 0, "message": "已取消"})
    else:
        return jsonify({"status": 1, "message": "车辆不存在"})