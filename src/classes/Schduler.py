from sortedcontainers import SortedSet
from src.classes.ChargingPile import ChargingPile
class Scheduler:
    fast_piles_num: int
    slow_piles_num: int
    piles: list
    def __init__(self):
        self.fast_piles_num = 0
        self.slow_piles_num = 0
        self.piles = list(list(), list())
        for pile in charging_piles:
            if pile.pile_type == PileType.Fast:
                self.fast_piles_num += 1
                self.piles[0].append(pile)
            else:
                self.slow_piles_num += 1
                self.piles[1].append(pile)
                
            

class FIFOScheduler(Scheduler):
    def __init__(self):
        super().__init__()
    def add_query(self, charge_mode, car_id) -> (bool, int):
        minimum_time = 1e9
        minimum_index = -1
        for pile in self.piles[charge_mode]:
            if pile.status == PileState.Idle or pile.status == PileState.Working:
                pile_time = 0
                if len(pile.cars_queue) < 2:
                    for info in pile.cars_queue:
                        pile_time = pile_time + (info.all_amount - info.changed_amount) / pile.charge_speed
                    if minimum_time > pile_time:
                        minimum_time = pile_time
                        minimum_index = pile.pile_id
        if minimum_index == -1:
            return False, -1
        else:
            request = get_charging_request(car_id)
            info = ChargingInfo(car_id, 0, request.amount, 0)
            self.piles[charge_mode][minimum_index].cars_queue.append(info)
            return True, minimum_index
    def shutdown_pile(self, charge_mode, pile_id):
        info_list = list()
        for info in self.piles[charge_mode][pile_id].cars_queue:
            info_list.append((get_charging_request(info.car_id).queue_num, ChargingInfo(info.car_id, 0, info.all_amount - info.changed_amount, 0)))
        self.piles[charge_mode][pile_id].cars_queue.clear()
        for pile in self.piles[charge_mode]:
            if pile.pile_id == pile_id:
                continue
            if len(pile.cars_queue) > 1:
                info = pile.cars_queue[1]
                info_list.append((get_charging_request(info.car_id).queue_num, info))
            pile.cars_queue.pop(1)
        info_list.sort(key = lambda x:x[0])
        for info in info_list:
            inserted = self.add_query(charge_mode, info.car_id)
            if inserted == False:
                # TODO: insert the query back to waiting area
                break