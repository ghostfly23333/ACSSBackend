# WARNING: NOT TESTED YET

from classes.ChargingPile import charging_piles, PileType, ChargingInfo, PileType, charging_piles, pile_callbacks, get_pile
from classes.ChargingRequest import get_charging_request, ChargingMode, get_charging_mode, get_charging_queue_num, get_charging_amount
import threading
from classes.Timer import timer
from config.sys import ScheduleMode,SCHEDULE_MODE
from classes.Bill import bill_manager


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
        waiting_cars = sorted(waiting_cars, key=lambda x: get_charging_request(x).queue_num)
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
            get_charging_request(car_id).reset_bill()
        try_request(mode)


    # 指定车辆退出等候区
    def exit(self, car_id: str):
        with queue_lock:
            try:
                if car_id in self.t_charging_queue:
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
            if SCHEDULE_MODE == ScheduleMode.NORMAL:
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
            if mode == ChargingMode.Ignore:
                if len(requests) < num:
                    return []
                else:
                    # 策略b
                    requests = sorted(requests, key=lambda x: get_charging_amount(x), reverse=True)
                    return requests
                       
            requests = sorted(requests, key=lambda x: get_charging_queue_num(x))
            return requests[:num] if len(requests) > num else requests

# 尝试叫号
try_lock = threading.Lock()
def try_request(mode:ChargingMode,num = 1):
    if mode is None:
        return
    # reset mode
    if SCHEDULE_MODE == ScheduleMode.GLOBAL_IGNORE_MODE:
        mode = ChargingMode.Ignore

    # reset num
    if SCHEDULE_MODE != ScheduleMode.NORMAL:
        num = vacant_num(mode)

    # assert vacant num
    if SCHEDULE_MODE == ScheduleMode.GLOBAL_LIMITED:
        if (mode == ChargingMode.Fast and num < 2) or (mode == ChargingMode.Normal and num < 3):
            return

    if waiting_area.calling_availale():
        with try_lock:
            firsts = waiting_area.get_first(mode, num)
            if len(firsts) > 0:
                if SCHEDULE_MODE == ScheduleMode.GLOBAL_IGNORE_MODE:
                    # 策略b
                    ## 快充调度
                    t_querys = sorted(firsts[:2*2], key=lambda x: get_charging_amount(x))
                    for t_query in t_querys:
                        get_charging_request(t_query).set_mode(ChargingMode.Fast)
                    scheduler.add_querys(t_querys)
                    ## 慢充调度
                    f_querys = sorted(firsts[2*2:], key=lambda x: get_charging_amount(x))     
                    for f_query in f_querys:
                        get_charging_request(f_query).set_mode(ChargingMode.Normal)                                  
                    scheduler.add_querys(f_querys)
                else:
                    scheduler.add_querys(firsts)



def pile_available_callback(mode: ChargingMode):
    try_request(mode,2)

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
            if charging_piles[minimum_index].queue_car(ChargingInfo(request.bill_id,car_id, request.amount)):
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
        results = list()
        for request in requests:
            results.append((request.car_id, self.add_query(request.car_id)))
        return results

    def shutdown_pile(self, charge_mode, pile_id):
        info_list = list()
        waiting_area.stop_calling()
        to_schedule_list = charging_piles[pile_id].shutdown()
        for info in to_schedule_list:
            info_list.append((get_charging_queue_num(info.car_id), info))
        
        for pile_index in self.piles[charge_mode.value]:
            pile = get_pile(pile_index)
            if pile.pile_id == pile_id:
                continue
            pile_queue = pile.clear_queue()
            for q in pile_queue:
                info_list.append((get_charging_queue_num(q.car_id), q))

        info_list.sort(key=lambda x: x[0][1:])

        for info in info_list:
            
            request = get_charging_request(info[1].car_id)
            if request is None:
                continue
            request.amount = request.amount - info[1].charged_amount
            bill_manager.find(info[1].bill_id).new(request.mode.value)
            inserted = self.add_query(info[1].car_id)
            if not inserted[0]:
                request.set_pile_id('')
                waiting_area.enter(info[1].car_id)
                break
        waiting_area.start_calling()


scheduler = FIFOScheduler()
