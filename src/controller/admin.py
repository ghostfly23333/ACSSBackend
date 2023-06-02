from flask import Blueprint, request, jsonify

app = Blueprint('admin_controller', __name__)

from classes.ChargingPile import charging_piles, PileState

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
        if pile.current_info is not None:
            return jsonify({
                "status": 0,
                "message": "查询成功",
                "data": {
                    "pile_id": pile.pile_id,
                    "status": pile.status.value,
                    "amount": pile.current_info.changed_amount,
                    "time": pile.current_info.changed_seconds,
                }
            })
        else:
            return jsonify({
                "status": 0,
                "message": "查询成功",
                "data": {
                    "pile_id": pile.pile_id,
                    "status": pile.status.value,
                }
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
    @apiParam {Int} status 充电桩状态 (0:关闭, 1:开启, 2:故障)
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
            or status is None or status not in [0, 1, 2]:
        return jsonify({
            "status": 1,
            "message": "参数错误",
        })
    
    if pile_id in charging_piles:
        pile = charging_piles[pile_id]
        pile.status = PileState(status)

        # TODO: reschedule

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
    pile_id = request.json.get('pile_id')
    if pile_id is None or not isinstance(pile_id, str):
        return jsonify({
            "status": 1,
            "message": "充电桩不存在",
        })
    if pile_id in charging_piles:
        pile = charging_piles[pile_id]
        cars_queue = pile.cars_queque
        cars_data = []
        for car_changingInfo in cars_queue[1:]: #不含正在充电的充电桩
            cars_data.append(jsonify({
                "pile_id": pile_id,
                "car" : car_changingInfo.car_id,
                "status": 0,
                "time"  : car_changingInfo.waited_seconds
            }))
        return jsonify({
            "status": 0,
            "message": "查询成功",
            "data" : cars_data,
        })
    return jsonify({
        "status": 1,
        "message": "token已过期",
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
    return 'admin/query/report'