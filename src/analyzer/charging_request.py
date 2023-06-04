from classes.ChargingRequest import ChargingRequest, request_dict, ChargingMode
from classes.ChargingPile import ChargingInfo, get_pile, is_charging
from classes.Schduler import waiting_area
from classes.Timer import timer


# 提交充电请求( 1: 提交成功  0: 提交失败 )
def submit_charging_request(user_id: str, car_id: str, mode: int,
                             amount: float) -> int:
    if car_id in request_dict:
        return 0
    else:
        # 提交请求
        request = ChargingRequest(user_id, car_id, ChargingMode(mode), amount)
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
            request_dict[car_id].set_mode(ChargingMode(mode))
            # 修改后重新生成排队号
            waiting_area.exit(car_id)    
            request_dict[car_id].set_queue_num(generate_queue_num())
            waiting_area.enter(car_id)   
            return 0
        else:
            # 在充电区
            # 取消充电后重新进入等候区排队
            user_id = request_dict[car_id].user_id
            amount = request_dict[car_id].amount
            submit_charging_request(user_id, car_id, mode, amount)
            cancel_charging_request(car_id)
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
            # 取消充电后重新进入等候区排队    
            user_id = request_dict[car_id].user_id
            mode = int(request_dict[car_id].mode)
            submit_charging_request(user_id, car_id, mode, amount)
            cancel_charging_request(car_id)
            return 2
    else:
        return 1
    
## 取消充电请求( 0: 取消成功  1: 车辆不存在 )
def cancel_charging_request(car_id) -> int:
    if car_id in request_dict:
        if is_charging(car_id) is False:
            # 未开始充电
            if waiting_area.is_waiting(car_id):
                # 在等候区
                waiting_area.exit(car_id)      
            else:
                # 在排队区
                # TODO 退出排队区
                pass      
            del request_dict[car_id]
        else:
            # 已终止充电过程
            end_charging_request(car_id)        
        return 0
    else:
        return 1
    

def query_charging_request(user_id: str) -> list:
    l = []
    for car in request_dict:
        if request_dict[car].user_id == user_id:
            l.append(car)
    return l

## 查询详单
def query_charging_detail(car_id: str) -> ChargingInfo:
    if car_id in request_dict:
        request = request_dict[car_id]
        pile_id = request.pile_id
        pile = get_pile(pile_id)
        
        info = None
        if pile is not None:
            info = pile.get_charging_info(car_id)
        else:
            pile_id = ""
        return {
            "car_id": car_id,
            "mode": request.mode.value,
            "status": info['status'] if info is not None else -1,
            "pile_id": pile_id,
            "request_amount": request.amount,
            "charged_amount": info['charged_amount'] if info is not None else 0,
            "duration": info['charged_seconds'] if info is not None else 0,
            "start_time": info['start_time'] if info is not None else "",
            "remain": info['time_remain'] if info is not None else -1
        }
    else:
        return None

        
# 根据系统当前时间生成排队号码(2023-01-01 00:00:00 -> 20230101060000 )
def generate_queue_num() -> str:
    now = timer.time()
    return "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(now.year,now.month,now.day,now.hour, now.minute, now.second)

# 移除充电请求，生成账单
def end_charging_request(car_id: str):
    if car_id in request_dict:
        # TODO: 生成账单

        del request_dict[car_id]