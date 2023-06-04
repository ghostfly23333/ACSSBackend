from enum import Enum


class ChargingMode(Enum):
    Normal = 0
    Fast = 1


class ChargingRequest:
    user_id: str
    car_id: str
    mode: ChargingMode
    amount: float
    queue_num: str
    pile_id: str

    def __init__(self, user_id: str, car_id: str, mode: ChargingMode, amount: float):
        self.user_id = user_id
        self.car_id = car_id
        self.mode = mode
        self.amount = amount
        self.pile_id = '',
        self.queue_num = -1

    def set_mode(self, mode: ChargingMode):
        self.mode = mode

    def set_amount(self, amount: float):
        self.amount = amount

    def set_queue_num(self, queue_num: str):
        self.queue_num = queue_num

    def set_pile_id(self, pile_id: str):
        self.pile_id = pile_id


# 索引为{car_id}的请求字典
request_dict = {}


def get_charging_request(car_id: str) -> ChargingRequest:
    if car_id in request_dict:
        return request_dict[car_id]
    else:
        return None
    
def get_charging_queue_num(car_id: str) -> str:
    req = request_dict.get(car_id)
    return req.queue_num if req is not None else None


def get_charging_mode(car_id: str) -> ChargingMode:
    req = request_dict.get(car_id)
    return req.mode if req is not None else None
