from src.classes.ChargingRequest import ChargingRequest
from analyzer.charging_request import get_charging_request

requests = list(str)

def add_request(r: str, force: bool = False) :
    if not force and len(requests) >= 6:
      return False
    requests.append(r) 
    return True

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


def notify_available(mode: int):
    r = get_request(mode)
    if r is not None:
      # scheduler
      pass


def notify_scheduled(r:str):
    # scheduler
    del requests[r]
    pass
        
      
        