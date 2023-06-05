from enum import Enum
from typing import Optional
from classes.Timer import timer, Time
from classes.ChargingRequest import del_charging_request
from classes.ChargingRequest import get_charging_queue_num, ChargingMode, get_charging_mode,get_charging_request,get_charging_request_user
from classes.Bill import compute_price,Bill,Bill_status
from analyzer.__init__ import container

import threading

class PileState(Enum):
    Idle = 0
    Working = 1
    Error = 2

class PileType(Enum):
    Normal = 0
    Fast = 1

# unit: 1 capacity per second
PILE_CHARGE_SPEED = {
    PileType.Fast: 30.0 / 3600,
    PileType.Normal: 7.0 / 3600
}


class ChargingInfo:
    car_id: str
    queue_num: str
    charged_amount: float
    all_amount: float
    charged_seconds: float
    waited_seconds: float
    start_time: Time
    status: int
    charge_speed: float
    fee: float

    base_amount: float
    base_seconds: float
    base_fee: float
    base_start_time: Time

    def __init__(self, car_id: str, all_amount: float):
        self.car_id = car_id
        self.all_amount = all_amount
        self.charged_amount = 0
        self.queue_num = get_charging_queue_num(car_id)
        self.charged_seconds = 0.0
        self.waited_seconds = 0.0
        #
        self.start_time = None
        self.status = 0
        self.charge_speed = 0.0
        self.fee = 0.0
    
    def __lt__(self, other):
        return self.queue_num < other.queue_num

    def start(self, charge_speed: float):
        self.start_time = timer.time()
        self.charge_speed = charge_speed
        self.status = 1

    def end(self):
        self.update()
        if self.all_amount <= self.charged_amount:
            self.status = 2
        else:
            self.status = 0

    def update(self):
        if self.status == 1:
            cur = timer.time()
            max_duration = cur - self.start_time
            max_amount = max_duration * self.charge_speed
            if max_amount  > self.all_amount:
                self.status = 2
                self.charged_amount = self.all_amount
                self.charged_seconds = self.all_amount / self.charge_speed
            else:
                self.charged_seconds = max_duration
                self.charged_amount = max_amount
            _, _, service_fee, charge_fee = compute_price(self.start_time, cur, get_charging_mode(self.car_id))
            self.fee = service_fee + charge_fee


    def time_remain(self) -> float:
        if self.status == 0:
            return -1
        elif self.status == 2:
            return 0.0
        cur = timer.time()
        return self.all_amount / self.charge_speed - (cur - self.start_time)
    
    def current(self):
        self.update()
        return self.to_dict()
    
    def current_result(self):
        self.update()
        return self.to_tuple_str()

    # to dict
    def to_dict(self) -> dict:
        return {
            "car_id": self.car_id,
            "user_id": get_charging_request_user(self.car_id),
            "status": self.status,
            "all_amount": self.all_amount,
            "queue_num": self.queue_num,
            "start_time": self.start_time.to_string() if self.start_time is not None else "",
            "time_remain": self.time_remain(),
            "charged_amount": self.charged_amount,
            "charged_seconds": self.charged_seconds,
            "fee": self.fee,
        }
    
    def to_tuple_str(self) -> str: 
        my_tuple = (self.car_id, "{:.2f}".format(self.charged_amount), "{:.2f}".format(self.fee))
        return '(' + ', '.join(map(str, my_tuple)) + ')'

pile_callbacks = []

class ChargingPile:
    pile_id: str
    pile_type: PileType
    charge_speed: float
    status: PileState
    cars_queue: list
    total_amount: float
    task_info: ChargingInfo
    task_id: int
    start_time: Time
    lock: threading.Lock

    def __init__(self, pile_id: str, pile_type: PileType):
        # metadata
        self.pile_id = pile_id
        self.pile_type = pile_type
        self.charge_speed = PILE_CHARGE_SPEED[pile_type]

        # runtime data
        self.status = PileState.Idle
        self.task_info = None
        self.total_amount = 0.0
        self.start_time = timer.time()
        self.cars_queue = list()
        self.task_id = -1
        self.lock = threading.Lock()
    
    def end_charging(self):
        end_time = timer.time()
        print(f'{end_time.to_string()} end charging: {self.task_info.car_id}')
        self.lock.acquire()
        if self.task_info is not None:
            self.task_info.end()
            self.total_amount += self.task_info.charged_amount
            request = get_charging_request(self.task_info.car_id)
            bill=Bill()
            bill.generate_request(request.user_id,self.pile_id,self.task_info.car_id,request.mode.value,self.task_info.charged_amount,self.task_info.start_time)
            bill.persist(end_time,Bill_status.Submitted,container)
            if self.task_info.status == 2:
                del_charging_request(self.task_info.car_id)
            self.task_info = None
            self.task_id = -1
            
        if self.status != PileState.Error:
            if len(self.cars_queue) == 0:
                self.status = PileState.Idle
                self.lock.release()
            else:
                self.lock.release()
                self.start_charging()

            for func in pile_callbacks:
                func(ChargingMode(self.pile_type.value))
        else:
            self.lock.release()
    
    def start_charging(self):
        with self.lock:
            if self.status == PileState.Error:
                return 
            if len(self.cars_queue) > 0 and self.task_info is None:
                self.task_info = self.cars_queue.pop(0)
                if self.task_info is None:
                    return
                
                print(f'start charging: {self.task_info.car_id} {self.task_info.all_amount}')
                self.status = PileState.Working
                interval = self.task_info.all_amount / self.charge_speed
                print(f'charge_speed: {self.charge_speed} interval:{interval}')
                self.task_info.start(self.charge_speed)
                self.task_id = timer.create_task(interval, self.end_charging, args=None)

    def cancel_charging(self, car_id: str):
        self.lock.acquire()
        if self.task_info is not None and self.task_info.car_id == car_id:
            self.lock.release()
            timer.cancel_task(self.task_id, run = True)
            del_charging_request(car_id)
        else:
            for item in self.cars_queue:
                if item.car_id == car_id:
                    self.cars_queue.remove(item)
                    item.end()
                    del_charging_request(car_id)
                    self.lock.release()
            

    def queue_car(self, info:ChargingInfo, forced: bool = False):
        if not forced and len(self.cars_queue) >= 1:
            return False
        with self.lock:
            self.cars_queue.append(info)

        if self.status == PileState.Idle:
            self.start_charging()
        return True
    

    def expected_finish_time(self) -> float:
        times = 0.0
        if self.task_info is not None:
            times += self.task_info.time_remain()

        for info in self.cars_queue:
            times += info.time_remain()

        return times
    
    def get_position(self, car_id: str) -> int:
        with self.lock:
            if self.task_info is not None and self.task_info.car_id == car_id:
                return 0
            for i in range(len(self.cars_queue)):
                if self.cars_queue[i].car_id == car_id:
                    return i + 1
            return -1


    def shutdown(self):
        with self.lock:
            self.status = PileState.Error
            self.start_time = None

            l = list(self.cars_queue)
            self.cars_queue = list()

            if self.task_info is not None:
                l.append(self.task_info)
        timer.cancel_task(self.task_id, run=True)
        return l
    

    def get_charging_info(self, car_id: str) -> Optional[ChargingInfo]:
        with self.lock:
            if self.task_info is not None and self.task_info.car_id == car_id:
                return self.task_info.current()
            for item in self.cars_queue:
                if item.car_id == car_id:
                    return item.current()
            return None
        
    def get_waiting_list(self) -> list:
        with self.lock:
            l = list(self.cars_queue)
            return [item.current() for item in l]
    
    def detail(self):
        res = {}
        with self.lock:
            if self.task_info is not None:
                res['charging'] = self.task_info.current()
            else:
                res['charging'] = None
            l = list(self.cars_queue)
            res['waiting'] = [item.current() for item in l]

            res['status'] = self.status.value
            res['amount'] = self.total_amount + (self.task_info.charged_amount if self.task_info is not None else 0) + sum([item.charged_amount for item in l])
            res['time'] = timer.time() - self.start_time if self.pile_type != PileState.Error and self.start_time is not None else 0
            return res
    
    def result(self):
        res = {}
        with self.lock:
            if self.task_info is not None:
                res['charging_area'] = self.task_info.current_result()
            else:
                res['charging_area'] = None
            l = list(self.cars_queue)
            for item in l:
                res['queuing_area'] = item.current_result()
            return res

    def clear_queue(self):
        with self.lock:
            l = list(self.cars_queue)
            self.cars_queue = list()
            return l

    def restart(self):
        if self.status != PileState.Error:
            return
        self.start_time = timer.time()
        self.cars_queue = list()
        self.task_id = -1
        self.status = PileState.Idle
        for func in pile_callbacks:
            func(ChargingMode(self.pile_type.value))

    def is_vacant(self) -> bool:
        with self.lock:
            return self.status != PileState.Error and len(self.cars_queue) == 0
    
    def get_maximum_available(self) -> int:
        result = 0
        if self.task_info is None:
            result += 1
        result += 1 - len(self.cars_queue)
        return result if result > 0 else 0

charging_piles = {
    "F1": ChargingPile("F1", PileType.Fast),
    "F2": ChargingPile("F2", PileType.Fast),
    "T1": ChargingPile("T1", PileType.Normal),
    "T2": ChargingPile("T2", PileType.Normal),
    "T3": ChargingPile("T3", PileType.Normal),
}


def get_pile(pile_id: str) -> Optional[ChargingPile]:
    if pile_id in charging_piles:
        return charging_piles[pile_id]
    else:
        return None
    
# 判断一辆车是否正在充电，若正在充电，则终止
def is_charging(car_id: str) -> bool:
    for _, pile in charging_piles.items():
        if pile.get_charging_info(car_id) is not None:
            return True           
    return False 



    

