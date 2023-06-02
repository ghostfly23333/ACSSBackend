from enum import Enum
class ChargingMode(Enum):
    Normal = 0
    Fast = 1

class ChargingRequest:
    user_id: str
    car_id: str
    mode: ChargingMode
    amount: float
    queue_num: int
    pile_id: str

    def __init__(self, user_id: str, car_id: str, mode: ChargingMode, amount: float):
        self.user_id = user_id
        self.car_id = car_id
        self.mode = mode
        self.amount = amount
        self.queue_num = 0      # 未分配排队号

    def set_mode(self, mode: int):
        self.mode = mode

    def set_amount(self, amount: float):
        self.amount = amount
    
    def set_queue_num(self, queue_num: int):
        self.queue_num = queue_num
    
    def set_pile_id(self, pile_id: str):
        self.pile_id = pile_id