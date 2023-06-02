# WARNING: NOT TESTED YET

from classes.ChargingPile import charging_piles, PileType, PileState, ChargingInfo
from classes.ChargingRequest import ChargingRequest
from analyzer.charging_request import get_charging_request
from classes.WaitingArea import waiting_area


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
                self.piles[0].append(pile.pile_id)
            else:
                self.slow_piles_num += 1
                self.piles[1].append(pile.pile_id)


class FIFOScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def add_query(self, charge_mode, car_id) -> (bool, int):
        minimum_time = 1e9
        minimum_index = -1
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
            request = get_charging_request(car_id)
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
