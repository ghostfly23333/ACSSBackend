from enum import Enum
from typing import Any, Callable, Optional
from threading import Lock
from classes.Timer import timer, Time
from classes.ChargingRequest import get_charging_queue_num
import queue
import threading
lock = Lock()

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
    
    def __lt__(self, other):
        return self.queue_num < other.queue_num

    def start(self, charge_speed: float):
        self.start_time = timer.time()
        self.charge_speed = charge_speed
        self.status = 1

    def end(self):
        self.update()
        self.status = 2

    def update(self):
        if self.status == 1:
            cur = timer.time()
            max_duration = cur - self.start_time
            max_amount = max_duration * self.charge_speed
            if max_amount > self.all_amount:
                self.status = 2
                self.charged_amount = self.all_amount
                self.charged_seconds = self.all_amount / self.charge_speed
            else:
                self.charged_seconds = max_duration
                self.charged_amount = max_amount

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

    # to dict
    def to_dict(self) -> dict:
        return {
            "car_id": self.car_id,
            "status": self.status,
            "all_amount": self.all_amount,
            "queue_num": self.queue_num,
            "start_time": self.start_time.to_string() if self.start_time is not None else "",
            "time_remain": self.time_remain(),
            "charged_amount": self.charged_amount,
            "charged_seconds": self.charged_seconds,
        }


pile_callbacks = []

class ChargingPile:
    pile_id: str
    pile_type: PileType
    charge_speed: float
    status: PileState

    cars_queue: queue.PriorityQueue()
    
    task_info: ChargingInfo
    task_id: int
    process_lock: threading.Lock

    def __init__(self, pile_id: str, pile_type: PileType):
        # metadata
        self.pile_id = pile_id
        self.pile_type = pile_type
        self.charge_speed = PILE_CHARGE_SPEED[pile_type]

        # runtime data
        self.status = PileState.Idle
        self.task_info = None
        self.cars_queue = queue.PriorityQueue()
        self.task_id = -1
        self.process_lock = threading.Lock()
    
    def end_charging(self):
        print(f'{timer.time().to_string()} end charging: {self.task_info.car_id}')
        self.process_lock.acquire()
        if self.task_info is not None:
            self.task_info.end()
            self.task_info = None

        if self.status != PileState.Error:
            if self.cars_queue.qsize() == 0:
                self.status = PileState.Idle
                self.process_lock.release()
            else:
                self.process_lock.release()
                self.start_charging()

            for func in pile_callbacks:
                func(self.pile_type)
    
    def start_charging(self):
        with self.process_lock:
            if self.status == PileState.Error:
                return 
            if self.cars_queue.qsize() > 0 and self.task_info is None:
                try:
                    self.task_info = self.cars_queue.get(False)
                except queue.Empty:
                    pass
                if self.task_info is None:
                    return
                print(f'start charging: {self.task_info.car_id} {self.task_info.all_amount}')
                self.status = PileState.Working
                interval = self.task_info.all_amount / self.charge_speed
                print(f'charge_speed:{self.charge_speed} interval:{interval}')
                self.task_info.start(self.charge_speed)
                self.task_id = timer.create_task(interval, self.end_charging, args=None)

    def queue_car(self, car_id: str, amount: float, forced: bool = False):
        if not forced and self.cars_queue.qsize() >= 1:
            return False
        self.cars_queue.put(ChargingInfo(car_id, amount))
        if self.status == PileState.Idle:
            self.start_charging()
        return True
    

    def expected_finish_time(self) -> float:
        times = 0.0
        if self.task_info is not None:
            times += self.task_info.time_remain()

        for info in self.cars_queue.queue:
            times += info.time_remain()

        return times


    def shutdown(self):
        with self.process_lock:
            self.status = PileState.Error
            if self.task_id != -1:
                timer.cancel_task(self.task_id)
                self.task_id = -1
            l = list(self.cars_queue.queue)
            if self.task_info is not None:
                l.append(self.task_info)
            self.task_info = None
            self.cars_queue = queue.PriorityQueue()
            return l
    

    def get_charging_info(self, car_id: str) -> Optional[ChargingInfo]:
        with self.process_lock:
            if self.task_info is not None and self.task_info.car_id == car_id:
                return self.task_info.current()
            for item in self.cars_queue.queue:
                if item.car_id == car_id:
                    return item.current()
            return None
    
    def detail(self):
        res = {}
        with self.process_lock:
            if self.task_info is not None:
                res['charging'] = self.task_info.current()
            else:
                res['charging'] = None
            l = list(self.cars_queue.queue)
            res['waiting'] = [item.current() for item in l]
            return res

        
    def clear_queue(self):
        with self.process_lock:
            l = list(self.cars_queue.queue)
            self.cars_queue = queue.PriorityQueue()
            return l

    def restart(self):
        if self.status != PileState.Error:
            return
        
        self.cars_queue = queue.PriorityQueue()
        self.task_id = -1
        self.status = PileState.Idle

    def is_vacant(self) -> bool:
        with lock:
            return self.status != PileState.Error and self.cars_queue.qsize() == 0

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
