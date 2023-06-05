# WARNING: NOT TESTED YET

from classes.ChargingPile import charging_piles, PileType, PileState, ChargingInfo, PileType, charging_piles, pile_callbacks, get_pile
from classes.ChargingRequest import get_charging_request, ChargingMode, get_charging_mode, get_charging_queue_num
import threading
from enum import Enum
from classes.Timer import timer, Time

class ScheduleMode(Enum):
    NORMAL = 0
    GLOBAL = 1
    GLOBAL_IGNORE_MODE = 2

schedule_mode = ScheduleMode.GLOBAL_IGNORE_MODE

calling_lock = threading.Lock()
queue_lock = threading.Lock()

class WaitingArea:
    calling: bool
    f_charging_queue: list
    t_charging_queue: list

    def __init__(self):
        self.calling = True
        self.f_charging_queue = []
        self.t_charging_queue = []

    def stop_calling(self):
        with calling_lock:
            self.calling = False
    
    def start_calling(self):
        with calling_lock:
            self.calling = True
        start_calling_callback()

    def calling_availale(self):
        with calling_lock:
            return self.calling
        
    def result(self) -> str:
        waiting_cars = self.f_charging_queue + self.t_charging_queue
        waiting_cars = sorted(waiting_cars, key=lambda x: int(get_charging_request(x).queue_num))
        result = ""
        for car_id in waiting_cars:
            request = get_charging_request(car_id)
            mode = 'T' if request.mode == ChargingMode.Normal else 'F'
            my_tuple = (car_id, mode, int(request.amount))
            if car_id != waiting_cars[0]:
                result += '-'            
            result += '(' + ', '.join(map(str, my_tuple)) + ')'
        return result

    # 指定车辆进入等候区
    def enter(self, car_id: str):
        mode = get_charging_mode(car_id)
        with queue_lock:
            if mode == ChargingMode.Normal:
                self.t_charging_queue.append(car_id)
            else:
                self.f_charging_queue.append(car_id)
        try_request(mode)


    # 指定车辆退出等候区
    def exit(self, car_id: str):
        mode = get_charging_mode(car_id)
        with queue_lock:
            try:
                if mode == ChargingMode.Normal:
                    self.t_charging_queue.remove(car_id)
                else:
                    self.f_charging_queue.remove(car_id)
            except ValueError:
                print("exit: ValueError")
                pass

    def get_waiting_list(self):
        with queue_lock:
            return list(self.f_charging_queue + self.t_charging_queue)

    # 判断指定车辆是否在等候区
    def is_waiting(self, car_id: str) -> bool:
        with queue_lock:
            if car_id in self.t_charging_queue or car_id in self.f_charging_queue:
                return True
            return False
    
    def get_queue_position(self, car_id: str) -> int:
        with queue_lock:
            cur_list = []
            if schedule_mode == ScheduleMode.NORMAL:
                if get_charging_mode(car_id) == ChargingMode.Normal:
                    cur_list = self.t_charging_queue
                else:
                    cur_list = self.f_charging_queue
            else:
                cur_list = self.f_charging_queue + self.t_charging_queue
            
            cur_list = sorted(cur_list, key=lambda x: get_charging_queue_num(x))
            pos = 0
            
            try:
                pos = cur_list.index(car_id)
            except ValueError:
                pos = -1
                pass

            return pos

    def get_first(self, mode: ChargingMode, num: int = 1):
        requests = []
        with queue_lock:
            if mode == ChargingMode.Ignore or mode == ChargingMode.Fast:
                for x in self.f_charging_queue:
                    requests.append(x)
            if mode == ChargingMode.Ignore or mode == ChargingMode.Normal:
                for x in self.t_charging_queue:
                    requests.append(x)
            if mode == ChargingMode.Ignore and len(requests) < num:
                return []
            
            requests = sorted(requests, key=lambda x: get_charging_queue_num(x))
            return requests[:num] if len(requests) > num else requests

# 尝试叫号
try_lock = threading.Lock()
def try_request(mode:ChargingMode):
    if mode is None:
        return
    # reset mode
    mode = ChargingMode.Ignore if schedule_mode == ScheduleMode.GLOBAL_IGNORE_MODE else mode
    # reset num
    num = 1 if schedule_mode == ScheduleMode.NORMAL else vacant_num(mode)
    print(f'vacant num: {num}')
    if waiting_area.calling_availale():
        with try_lock:
            firsts = waiting_area.get_first(mode,num)
            if len(firsts) > 0:
                scheduler.add_querys(firsts)


def pile_available_callback(mode: ChargingMode):
    try_request(mode)

pile_callbacks.append(pile_available_callback)
      
def start_calling_callback():
    try_request(ChargingMode.Fast)
    try_request(ChargingMode.Normal)

def vacant_num(mode: ChargingMode) -> bool:
    available = 0
    if mode == ChargingMode.Fast or mode == ChargingMode.Ignore:
        available += scheduler.get_maximum_available(ChargingMode.Fast)
    if mode == ChargingMode.Normal or mode == ChargingMode.Ignore:
        available += scheduler.get_maximum_available(ChargingMode.Normal)
    return available

waiting_area = WaitingArea()

class Scheduler:
    fast_piles_num: int
    slow_piles_num: int
    piles: list

    def __init__(self):
        self.fast_piles_num = 0
        self.slow_piles_num = 0
        self.piles = [list(), list()]
        for _, pile in charging_piles.items():
            if pile.pile_type == PileType.Fast:
                self.fast_piles_num += 1
                self.piles[1].append(pile.pile_id)
            else:
                self.slow_piles_num += 1
                self.piles[0].append(pile.pile_id)


class FIFOScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def add_query(self, car_id):
        minimum_time = 1e9
        minimum_index = -1
        request = get_charging_request(car_id)
        if request is None:
            return False, -1
        
        charge_mode = request.mode

        for pile_index in self.piles[charge_mode.value]:
            pile = get_pile(pile_index)
            if pile.is_vacant():             
                pile_time = pile.expected_finish_time()  
                if pile_time < 5.0:
                    pile_time = 0.0                     
                if minimum_time > pile_time:
                    minimum_time = pile_time
                    minimum_index = pile.pile_id
        if minimum_index == -1:
            return False, -1
        else:
            request.set_pile_id(minimum_index)
            print(f'{timer.time().to_string()} new car: {car_id}')
            if charging_piles[minimum_index].queue_car(car_id, request.amount):
                waiting_area.exit(car_id)
                return True, minimum_index
            else:
                return False, -1

    def get_maximum_available(self, charge_mode) -> int:
        result = 0
        for pile_index in self.piles[charge_mode.value]:
            pile = get_pile(pile_index)
            result += pile.get_maximum_available()
        return result


    def add_querys(self, car_ids) -> list:
        requests = list(get_charging_request(x) for x in car_ids)
        requests.sort(key=lambda x: x.amount)
        results = list()
        for request in requests:
            results.append((request.car_id, self.add_query(request.car_id)))
        return results

    def shutdown_pile(self, charge_mode, pile_id):
        info_list = list()
        # TODO : wirte generate bill in end_charing() at ChargingPile.py
        waiting_area.stop_calling()
        to_schedule_list = charging_piles[pile_id].shutdown()
        for info in to_schedule_list:
            new_info = info.relay()
            info_list.append((get_charging_request(info.car_id).queue_num, new_info))
        
        for pile_index in self.piles[charge_mode.value]:
            pile = get_pile(pile_index)
            if pile.pile_id == pile_id:
                continue
            pile_queue = pile.clear_queue()
            for q in pile_queue:
                info_list.append((get_charging_request(q.car_id).queue_num, q))

        info_list.sort(key=lambda x: x[0][1:])

        for info in info_list:
            inserted = self.add_query(info[1].car_id)
            request = get_charging_request(info[1].car_id)
            if not inserted[0]:
                request.set_pile_id(0)
                waiting_area.enter(info[1].car_id)
                break
            else:
                request.set_pile_id(info[1].car_id)
        waiting_area.start_calling()


scheduler = FIFOScheduler()
