from flask import Blueprint, request, jsonify
from analyzer.charging_request import query_waiting_list
from classes.ChargingRequest import ChargingMode
from classes.Schduler import scheduler
from classes.ChargingPile import charging_piles
from classes.Timer import Time

app = Blueprint('admin_controller', __name__)

from classes.ChargingPile import charging_piles, PileState
from analyzer.__init__ import container

@app.route('/query/state', methods=['GET'])
def query_state():
    """
    @api {get} /admin/query/state 查询充电桩状态
    @apiName QueryState
    @apiGroup Admin
    @apiParam {String} pile_id 充电桩id(不选则查询所有充电桩)
    @apiSuccess {String} pile_id 充电桩id
    @apiSuccess {Int} status 充电桩状态 (0:空闲, 1:正在充电, 2:故障)
    @apiSuccess {Double} amount 已充电量
    @apiSuccess {Double} time 运行时间
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": [
          {
            "pile_id": "",
            "status": 0,
            "amount": 0,
            "time": 0
          }
        ]
      } 
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 200 OK
      {
        "status": 1,
        "message": "充电桩不存在"
      }
    """

    pile_id = request.args.get('pile_id')
    if pile_id is None or not isinstance(pile_id, str):
        return jsonify({
            "status": 1,
            "message": "参数错误",
        })

    if pile_id in charging_piles:
        pile = charging_piles[pile_id]
        res = pile.detail()
        res['pile_id'] = pile_id
        return jsonify({
            "status": 0,
            "message": "查询成功",
            "data": res,
        })
    
    return jsonify({
        "status": 1,
        "message": "充电桩不存在",
    })


@app.route('/alter/pile', methods=['POST'])
def alter_pile():
    """
    @api {post} /admin/alter/pile 修改充电桩状态
    @apiName AlterPile
    @apiGroup Admin
    @apiParam {String} pile_id 充电桩id
    @apiParam {Int} status 充电桩状态 (0:关闭, 1:开启)
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
        "message": "充电桩不存在"
      }
    """
    pile_id = request.json.get('pile_id')
    status = request.json.get('status')
    if pile_id is None or not isinstance(pile_id, str) \
            or status is None or status not in [0, 1]:
        return jsonify({
            "status": 1,
            "message": "参数错误",
        })
    
    if pile_id in charging_piles:
        pile = charging_piles[pile_id]
        if pile.status != PileState.Error and status == 0:
            scheduler.shutdown_pile(ChargingMode(pile.pile_type.value), pile.pile_id)
        elif pile.status == PileState.Error and status == 1:
            pile.restart()
        else:
            return jsonify({
                "status": 1,
                "message": "重复的操作",
            })
        return jsonify({
            "status": 0,
            "message": "修改成功",
        })
    
    return jsonify({
        "status": 1,
        "message": "充电桩不存在",
    })


@app.route('/query/waitlist', methods=['GET'])
def query_waitlist():
    """
    @api {get} /admin/query/waitlist 查询等待区
    @apiName QueryWaitlist
    @apiGroup Admin
    @apiSuccess {String} car_id 车辆id
    @apiSuccess {Int} mode 充电模式 (1:快充, 0:慢充)
    @apiSuccess {Double} amount 充电量
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": [
          {
            "car_id": "",
            "mode": 0,
            "amount": 0
          }
        ]
      }
    """
    l = query_waiting_list()
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": l,
    })


@app.route('/query/pile/waitlist', methods=['GET'])
def query_pile_waitlist():
    """
    @api {get} /admin/query/pile/waitlist 查询充电桩等待队列
    @apiName QueryWaitlist
    @apiGroup Admin
    @apiParam {String} pile_id 充电桩id
    @apiSuccess {String} user_id 用户id
    @apiSuccess {String} car 车辆id
    @apiSuccess {Int} status 状态(0:等待中, 1:已取消)
    @apiSuccess {String} time 时间
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": [
          {
            "pile_id": "",
            "car": "",
            "status": 0,
            "time": ""
          }
        ]
      } 
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 401 UNAUTHORIZED
      {
        "status": 1,
        "message": "token已过期"
      }
    """
    pile_id = request.args.get('pile_id')
    if pile_id is None or not isinstance(pile_id, str):
        return jsonify({
            "status": 1,
            "message": "充电桩不存在",
        })
    if pile_id in charging_piles:
        pile = charging_piles[pile_id]
        waiting_list = pile.get_waiting_list()
        return jsonify({
            "status": 0,
            "message": "查询成功",
            "data" : waiting_list,
        })
    return jsonify({
        "status": 1,
        "message": "充电桩不存在",
    })



@app.route('/query/report', methods=['GET'])
def query_report():
    """
    @api {get} /admin/query/report 查询报表
    @apiName QueryReport
    @apiGroup Admin
    @apiParam {String} start 开始日期
    @apiParam {String} end 结束日期
    @apiSuccess {String} start 开始日期
    @apiSuccess {String} end 结束日期
    @apiSuccess {String} duration 总时间
    @apiSuccess {Double} amount 总电量
    @apiSuccess {Double} service 服务费
    @apiSuccess {Double} charge 充电费用
    @apiSuccess {Double} total 总费用
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": 0,
        "message": "查询成功",
        "data": {
          "start": "",
          "end": "",
          "duration": 0,
          "date": "",
          "amount": 0,
          "service": 0,
          "charge": 0,
          "total": 0
        }
      } 
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 401 UNAUTHORIZED
      {
        "status": 1,
        "message": "token已过期"
      }
    """
    start = request.args.get('start')
    end = request.args.get('end')
    duration,amount,service,charge,total=0,0,0,0,0
    try:
      start = Time.make(start).stamp if start != "" else 0.0
      end = Time.make(end).stamp if end != "" else 0.0
    except:
      return jsonify({
        "status": 1,
        "message": "日期格式错误",
      })
    
    min_start = 0.0
    max_end = 0.0
    for content in container.all_bills():
        if (start == 0.0 or content['start_time'] >= start) and (end == 0.0 or content['end_time'] <= end):
            if min_start == 0.0 or content['start_time'] < min_start:
                min_start = content['start_time']
            if max_end == 0.0 or content['end_time'] > max_end:
                max_end = content['end_time']
            duration+=content['duration']
            amount+=content['amount']
            service+=content['service_cost']
            charge+=content['charge']
            total+=content['total']

    start = start if start != 0.0 else min_start
    end = end if end != 0.0 else max_end
      
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": {
          "start": Time(start).to_string() if start != 0.0 else "",
          "end": Time(end).to_string() if end != 0.0 else "",
          "duration": duration,
          "amount": amount,
          "service": service,
          "charge": charge,
          "total": total
        }
      })

