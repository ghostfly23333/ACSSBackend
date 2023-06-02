from enum import Enum
from typing import Callable, Optional
from threading import Lock
lock = Lock()

class PileState(Enum):
    Idle = 0
    Working = 1
    Error = 2


class PileType(Enum):
    Normal = 0
    Fast = 1

# unit: 1 capacity per second
PILE_CHARGE_SPEED = {
    PileType.Fast: 60.0,
    PileType.Normal: 30.0
}


class ChargingInfo:
    car_id: str
    charged_amount: float
    all_amount: float
    charged_seconds: float
    waited_seconds: float

    def __init__(self, car_id: str, all_amount: float):
        self.car_id = car_id
        self.all_amount = all_amount
        self.charged_amount = 0
        self.charged_seconds = 0.0
        self.waited_seconds = 0.0

pile_callbacks: list[Callable[[PileType], None]] = []

class ChargingPile:
    pile_id: str
    pile_type: PileType
    charge_speed: float
    status: PileState
    cars_queue: list

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
    def current_info(self) -> Optional[ChargingInfo]:
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
            self.current_info.charged_seconds += seconds
            self.current_info.charged_amount += self.charge_speed * seconds
            if self.current_info.charged_amount >= self.current_info.all_amount:
                uid = self.current_info.car_id
                self.cars_queue.pop(0)
                if len(self.cars_queue) == 0:
                    self.status = PileState.Idle
                for func in pile_callbacks:
                    func(self.pile_type)
                return uid
        return None

    def queue_car(self, car_id: str, capacity: float):
        self.cars_queue.append(ChargingInfo(car_id, capacity))
        if self.status == PileState.Idle:
            self.status = PileState.Working

    def is_vacant(self) -> bool:
        with lock:
            return self.status != PileState.Error and len(self.cars_queue) < 2

charging_piles = {
    "1": ChargingPile("1", PileType.Fast),
    "2": ChargingPile("2", PileType.Fast),
    "3": ChargingPile("3", PileType.Normal),
    "4": ChargingPile("4", PileType.Normal),
    "5": ChargingPile("5", PileType.Normal),
}
