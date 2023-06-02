from enum import Enum
from typing import Optional


class PileState(Enum):
    Idle = 0
    Working = 1
    Error = 2


class PileType(Enum):
    Fast = 0
    Normal = 1

# unit: 1 capacity per second
PILE_CHARGE_SPEED = {
    PileType.Fast: 60.0,
    PileType.Normal: 30.0
}


class ChangingInfo:
    car_id: int
    changed_amount: float
    all_amount: float
    changed_seconds: float
    waited_seconds: float

    def __init__(self, car_id: int, all_amount: float):
        self.car_id = car_id
        self.all_amount = all_amount
        self.changed_amount = 0
        self.changed_seconds = 0.0
        self.waited_seconds = 0.0


class ChargingPile:
    pile_id: str
    pile_type: PileType
    charge_speed: float
    status: PileState
    cars_queue: list[ChangingInfo]

    def __init__(self, pile_id: str, pile_type: PileType):
        # metadata
        self.pile_id = pile_id
        self.pile_type = pile_type
        self.charge_speed = PILE_CHARGE_SPEED[pile_type]

        # runtime data
        self.status = PileState.Idle
        self.cars_queue = []

    def __str__(self):
        return f"Charging pile {self.pile_id}: with {self.status} status and speed = {self.charge_speed}"
    
    @property
    def current_info(self) -> Optional[ChangingInfo]:
        if len(self.cars_queue) > 0:
            return self.cars_queue[0]
        return None

    # for use in timer thread, should be called every time slot
    # return car_id if a user is charged full, else return None
    def time_passed(self, seconds: float):
        if len(self.cars_queue) > 1:
            for waiting_car in self.cars_queue[1:]:
                waiting_car.waited_seconds += seconds

        if self.current_info is not None:
            self.current_info.changed_seconds += seconds
            self.current_info.changed_amount += self.charge_speed * seconds
            if self.current_info.changed_amount >= self.current_info.all_amount:
                uid = self.current_info.car_id
                self.cars_queue.pop(0)
                if len(self.cars_queue) == 0:
                    self.status = PileState.Idle
                return uid
        return None

    def queue_car(self, car_id: int, capacity: float):
        self.cars_queue.append(ChangingInfo(car_id, capacity))
        if self.status == PileState.Idle:
            self.status = PileState.Working

charging_piles = {
    "1": ChargingPile("1", PileType.Fast),
    "2": ChargingPile("2", PileType.Fast),
    "3": ChargingPile("3", PileType.Normal),
    "4": ChargingPile("4", PileType.Normal),
    "5": ChargingPile("5", PileType.Normal),
    "6": ChargingPile("6", PileType.Normal),

}
