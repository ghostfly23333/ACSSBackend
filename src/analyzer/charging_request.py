from classes.ChargingRequest import ChargingRequest, request_dict
from classes.Schduler import waiting_area
from classes.Timer import timer


# 提交充电请求( 1: 提交成功  0: 提交失败 )
def submit_charging_request(user_id: str, car_id: str, mode: int,
                             amount: float) -> int:
    if car_id in request_dict:
        return 0
    else:
        # 提交请求
        request = ChargingRequest(user_id, car_id, mode, amount)
        request.set_queue_num(generate_queue_num())
        request_dict[car_id] = request
        waiting_area.enter(car_id)
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
            request_dict[car_id].set_queue_num(generate_queue_num())
            waiting_area.enter(car_id)   
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
        waiting_area.exit(car_id)
        del request_dict[car_id]
        return 0
    else:
        return 1
        

# 根据系统当前时间生成排队号码( 6:00:00 -> 060000 )
def generate_queue_num() -> str:
    now = timer.time()
    return "{:02d}{:02d}{:02d}".format(now.hour, now.minute, now.second)