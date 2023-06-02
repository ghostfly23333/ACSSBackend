import queue


class WaitingArea:
    size: int
    f_charging_queue: queue[str]
    t_charging_queue: queue[str]


    def __init__(self, size: int):
        self.size = size
        self.f_charging_queue = []
        self.t_charging_queue = []