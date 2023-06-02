from ChargingRequest import ChargingMode
from analyzer.charging_request import get_charging_mode
from analyzer.scheduler_call import try_request, start_calling_callback
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
        

    # 指定车辆退出等候区，并修改排在其后的车辆的排队号码
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


waiting_area = WaitingArea(6)
