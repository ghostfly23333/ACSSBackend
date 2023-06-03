# WARNING: NOT TESTED YET

from classes.ChargingPile import charging_piles, PileType, PileState, ChargingInfo, PileType, charging_piles, pile_callbacks
from classes.ChargingRequest import get_charging_request, ChargingMode, get_charging_mode
import threading
from classes.Timer import timer, Time

calling_lock = threading.Lock()

class WaitingArea:
    size: int
    calling: bool
    f_charging_queue: list
    t_charging_queue: list

    def __init__(self, size: int):
        self.size = size
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
    
    # 指定车辆进入等候区
    def enter(self, car_id: str):
        mode = get_charging_mode(car_id)
        if mode == ChargingMode.Normal:
            self.t_charging_queue.append(car_id)
        else:
            self.f_charging_queue.append(car_id)
        try_request(mode)


    # 指定车辆退出等候区
    def exit(self, car_id: str):
        mode = get_charging_mode(car_id)
        try:
            if mode == ChargingMode.Normal:
                self.t_charging_queue.remove(car_id)
            else:
                self.f_charging_queue.remove(car_id)
        except ValueError:
            print("exit: ValueError")
            pass

    # 判断指定车辆是否在等候区
    def is_waiting(self, car_id: str) -> bool:
        if car_id in self.t_charging_queue or car_id in self.f_charging_queue:
            return True
        return False
    

    def get_first(self, mode: ChargingMode):
        #print(mode == ChargingMode.Fast)
        #print(mode, ChargingMode.Fast)
        queue = self.f_charging_queue if mode == ChargingMode.Fast else self.t_charging_queue
        requests = list(get_charging_request(x) for x in queue)
        sorted(requests, key=lambda x: x.queue_num)
        #print(len(self.f_charging_queue), len(self.t_charging_queue))
        #print(len(requests))
        return requests[0].car_id if len(requests) != 0 else None

# 尝试叫号
try_lock = threading.Lock()
def try_request(mode:ChargingMode):
    if mode is None:
        return
    if waiting_area.calling_availale():
        with try_lock:
            r = waiting_area.get_first(mode)
            if r is not None and is_vacant(mode):
                scheduler.add_query(r)


def pile_available_callback(mode: ChargingMode):
    try_request(mode)

pile_callbacks.append(pile_available_callback)

      
def start_calling_callback():
    try_request(ChargingMode.Fast)
    try_request(ChargingMode.Normal)

def is_vacant(mode: ChargingMode) -> bool:
    if mode == ChargingMode.Fast:
        return charging_piles["F1"].is_vacant() or charging_piles["F2"].is_vacant()
    elif mode == ChargingMode.Normal:
        return charging_piles["T1"].is_vacant() or charging_piles["T2"].is_vacant() or charging_piles["T3"].is_vacant()
    else:
        return False

waiting_area = WaitingArea(6)



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
            pile = charging_piles[pile_index]
            if pile.is_vacant():
                pile_time = pile.expected_finish_time()
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

    def shutdown_pile(self, charge_mode, pile_id):
        info_list = list()
        # TODO : wirte generate bill in end_charing() at ChargingPile.py
        to_schedule_list = charging_piles[pile_id].shutdown()
        for info in to_schedule_list:
            info_list.append((get_charging_request(info.car_id).queue_num, 
                             ChargingInfo(info.car_id, info.all_amount - info.charged_amount)))
        
        for pile_index in self.piles[charge_mode.value]:
            pile = charging_piles[pile_index]
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


scheduler = FIFOScheduler()
