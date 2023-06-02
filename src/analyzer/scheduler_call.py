from classes.ChargingRequest import ChargingRequest
from analyzer.charging_request import get_charging_request
from classes.ChargingPile import is_vacant
import threading
lock = threading.Lock()
requests = list(str)

def add_request(r: str, force: bool = False) :
    with lock:
      if not force and len(requests) >= 6:
        return False
      requests.append(r)
      threading.Thread(target=process_new_request(r)).start()
      return True


def process_new_request(r:str):
    req = get_charging_request(r)
    if req is None:
        return
    if is_vacant(req.mode):
        # scheduler
        pass
    


def get_request(mode: int):
    min = 0
    ret = None
    for r in requests:
        if r.mode == mode:
            req = get_charging_request(r)
            if req.queue_num < min:
                min = req.queue_num
                ret = r
    return ret if min != 0 else None


def call_scheduler():
    # scheduler
    pass

# for use in end of charging
def notify_available(mode: int):
    r = get_request(mode)
    if r is not None:
      # scheduler
      pass

# for use in end of scheduling

def notify_scheduled(r:str):
    # scheduler
    del requests[r]
    pass
        
      
        