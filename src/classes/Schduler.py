# WARNING: NOT TESTED YET

from classes.ChargingPile import charging_piles, PileType, PileState, ChargingInfo, PileType, charging_piles, pile_callbacks
from classes.ChargingRequest import get_charging_request, ChargingMode, get_charging_mode
from threading import Lock

calling_lock = Lock()

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
            self.f_charging_queue.append(car_id)
        else:
            self.f_charging_queue.append(car_id)
        try_request(mode)
        

    # 指定车辆退出等候区
    def exit(self, car_id: str):
        mode = get_charging_mode(car_id)
        try:
            if mode == ChargingMode.Normal:
                self.f_charging_queue.remove(car_id)
            else:
                self.t_charging_queue.remove(car_id)
        except ValueError:
            pass

    # 判断指定车辆是否在等候区
    def is_waiting(self, car_id: str) -> bool:
        if car_id in self.t_charging_queue or car_id in self.f_charging_queue:
            return True
        return False
    

    def get_first(self, mode: ChargingMode):
        requests = self.f_charging_queue if mode == ChargingMode.Fast else self.t_charging_queue
        sorted(requests, key=lambda x: requests[x].queue_num)
        return requests[0] if len(requests) != 0 else None

def try_request(mode:ChargingMode):
    if mode is None:
        return
    if waiting_area.calling_availale() and is_vacant(mode):
        r = waiting_area.get_first(mode)
        scheduler.add_query(r)

    
def pile_available_callback(mode: ChargingMode):
    try_request(mode)

pile_callbacks.append(pile_available_callback)

      
def start_calling_callback():
    try_request(ChargingMode.Fast)
    try_request(ChargingMode.Normal)

def is_vacant(mode: int) -> bool:
    if mode == PileType.Fast:
        return charging_piles["1"].is_vacant() or charging_piles["2"].is_vacant()
    elif mode == PileType.Normal:
        return charging_piles["3"].is_vacant() or charging_piles["4"].is_vacant() or charging_piles["5"].is_vacant()
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

        for pile_index in self.piles[charge_mode]:
            pile = charging_piles[pile_index]
            if pile.status == PileState.Idle or pile.status == PileState.Working:
                pile_time = 0
                if len(pile.cars_queue) < 2:
                    for info in pile.cars_queue:
                        pile_time = pile_time + (info.all_amount - info.charged_amount) / pile.charge_speed
                    if minimum_time > pile_time:
                        minimum_time = pile_time
                        minimum_index = pile.pile_id
        if minimum_index == -1:
            return False, -1
        else:
            info = ChargingInfo(car_id, request.amount)
            charging_piles[minimum_index].cars_queue.append(info)
            return True, minimum_index

    def shutdown_pile(self, charge_mode, pile_id):
        info_list = list()
        for info in charging_piles[pile_id].cars_queue:
            # TODO: generate bill
            info_list.append((get_charging_request(info.car_id).queue_num,
                              ChargingInfo(info.car_id, info.all_amount - info.charged_amount)))
        charging_piles[pile_id].cars_queue.clear()
        for pile_index in self.piles[charge_mode]:
            pile = charging_piles[pile_index]
            if pile.pile_id == pile_id:
                continue
            if len(pile.cars_queue) > 1:
                info = pile.cars_queue[1]
                info_list.append((get_charging_request(info.car_id).queue_num, info))
            pile.cars_queue.pop(1)
        info_list.sort(key=lambda x: x[0][1:])
        for info in info_list:
            inserted = self.add_query(charge_mode, info[1].car_id)
            request = get_charging_request(info[1].car_id)
            if not inserted[0]:
                request.set_pile_id(0)
                waiting_area.enter(info[1].car_id, charge_mode)
                break
            else:
                request.set_pile_id(inserted.second)


scheduler = FIFOScheduler()
