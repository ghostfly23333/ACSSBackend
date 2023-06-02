from src.classes import ChargingRequest
from src.classes import waiting_area


# 索引为{car_id}的请求字典
request_dict = {}


# 提交充电请求( 1: 提交成功  0: 提交失败 )
def submit_charging_request(user_id: str, car_id: str, mode: int,
                             amount: float) -> int:
    if car_id in request_dict:
        return 0
    else:
        # 此时不存在该请求
        request = ChargingRequest(user_id, car_id, mode, amount)
        waiting_area.enter(car_id, mode)
        request.set_queue_num(generate_queue_num(mode))
        request_dict[car_id] = request
        return 1
        

# 修改充电请求
## 修改充电模式( 0: 修改成功  1: 车辆不存在  2: 不允许修改)
def alter_charging_mode(car_id: str, mode: int) -> int:
    if car_id in request_dict:
        if waiting_area.is_waiting(car_id):
            # 在等候区
            request_dict[car_id].set_mode(mode)
            # 修改后重新生成排队号
            waiting_area.exit(car_id)
            request_dict[car_id].set_queue_num(generate_queue_num(mode))
            return 0
        else:
            # 在充电区
            # TODO: 不允许修改，可取消充电后 离开 / 重新进入等候区排队
            return 2
    else:
        return 1
    

## 修改充电量( 0: 修改成功  1: 车辆不存在  2: 不允许修改)
def alter_charging_amount(car_id: str, amount: float) -> int:
    if car_id in request_dict:
        if waiting_area.is_waiting(car_id):
            # 在等候区: 允许修改
            request_dict[car_id].set_amount(amount)
            return 0
        else:
            # 在充电区
            # TODO: 不允许修改，可取消充电后 离开 / 重新进入等候区排队
            return 2
    else:
        return 1


## 取消充电请求( 0: 取消成功  1: 车辆不存在 )
def cancel_charging_request(car_id) -> int:
    if car_id in request_dict:
        del request_dict[car_id]
        return 0
    else:
        return 1
        

# 查找充电请求
def get_charging_request(car_id: str) -> ChargingRequest: 
    return request_dict.get(car_id)


# 生成排队号码
def generate_queue_num(mode: int) -> int:
    if mode == 0:
        # 慢速
        return waiting_area.t_charging_queue.qsize()
    else:
        # 快速
        return waiting_area.f_charging_queue.qsize()