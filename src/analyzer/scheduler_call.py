from classes.ChargingRequest import ChargingMode
from classes.WaitingArea import waiting_area
from classes.ChargingPile import is_vacant
from classes.Schduler import scheduler
import threading

def try_request(mode:ChargingMode):
    if mode is None:
        return
    if waiting_area.calling_availale() and is_vacant(mode):
        r = waiting_area.get_first(mode)
        scheduler.add_query(r)

    
def pile_available_callback(mode:ChargingMode):
    try_request(mode)
      
      
def start_calling_callback():
    try_request(ChargingMode.Fast)
    try_request(ChargingMode.Normal)