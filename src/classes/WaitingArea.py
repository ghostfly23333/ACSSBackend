class WaitingArea:
    size: int
    f_charging_queue: list[str]
    t_charging_queue: list[str]

    def __init__(self, size: int):
        self.size = size
        self.f_charging_queue = list()
        self.t_charging_queue = list()

    # 指定车辆进入等候区
    def enter(self, car_id: str, mode: int):
        if mode == 0:
            # 慢速
            self.t_charging_queue.append(car_id)
        else:
            # 快速
            self.f_charging_queue.append(car_id)

    # 指定车辆退出等候区
    def exit(self, car_id: str, mode: int):
        if mode == 0:
            self.t_charging_queue.remove(car_id)
        else:
            self.f_charging_queue.remove(car_id)

    # 判断指定车辆是否在等候区
    def is_waiting(self, car_id: str) -> bool:
        if car_id in self.t_charging_queue or car_id in self.f_charging_queue:
            return True
        return False


waiting_area = WaitingArea(6)
