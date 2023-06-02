class WaitingArea:
    size: int
    f_charging_queue: list
    t_charging_queue: list

    def __init__(self, size: int):
        self.size = size
        self.f_charging_queue = []
        self.t_charging_queue = []
    
    # 指定车辆进入等候区
    def enter(self, car_id: str, mode: int):
        if mode == 0:
            # 慢速
            self.t_charging_queue.append(car_id)
        else:
            # 快速
            self.f_charging_queue.append(car_id)

    # 指定车辆退出等候区，并修改排在其后的车辆的排队号码
    def exit(self, car_id: str, mode: int, request_dict: dict):
        if mode == 0:
            exit_car_index = self.t_charging_queue.index(car_id)
            for i in range(exit_car_index, len(self.t_charging_queue)):
                # 修改排队号
                request_dict[self.t_charging_queue[i]].queue_num -= 1
            self.t_charging_queue.remove(car_id)   
        else:
            exit_car_index = self.f_charging_queue.index(car_id)
            for i in range(exit_car_index, len(self.f_charging_queue)):
                request_dict[self.f_charging_queue[i]].queue_num -= 1
            self.f_charging_queue.remove(car_id)

    # 判断指定车辆是否在等候区
    def is_waiting(self, car_id: str) -> bool:
        if car_id in self.t_charging_queue or car_id in self.f_charging_queue:
            return True
        return False


waiting_area = WaitingArea(6)
