import time
import threading

SYSTEM_TIME_RATIO = 20

class Time:
    stamp:float
    year:int
    month:int
    day:int
    hour:int
    minute:int
    second:int

    def __init__(self, stamp:float):
        self.stamp = stamp
        tm_struct = time.localtime(stamp)
        self.year = tm_struct.tm_year
        self.month = tm_struct.tm_mon
        self.day = tm_struct.tm_mday
        self.hour = tm_struct.tm_hour
        self.minute = tm_struct.tm_min
        self.second = tm_struct.tm_sec

    def make(time_str:str):
        stamp = time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
        return Time(stamp)

    def __str__(self) -> str:
        time_str = '%02d-%02d-%02d %02d:%02d:%02d' % (self.year, self.month, self.day, self.hour, self.minute, self.second)
        return time_str

    def to_string(self) -> str:
        return self.__str__()
    
    def __sub__(self, other) -> float:
        return abs(self.stamp - other.stamp)
    

class Timer:
    system_base_time : float
    base_time : float
    task_id: int
    lock = threading.Lock()
    dict_lock = threading.Lock()
    tasks : dict
    ratio : int
    # 初始化
    def __init__(self, ratio:int = 1, base:Time = None) -> None:
        self.system_base_time = time.time()
        if base is None:
            self.base_time = self.system_base_time
        else:
            self.base_time = base.stamp
            print(self.base_time)
        self.ratio = ratio
        self.task_id = 0
        self.tasks = {}
    
    # 任务id
    def __task_id(self):
        with self.lock:
            self.task_id += 1
            return self.task_id

    # 定时任务回调
    def __callback(self, uid):
        if uid not in self.tasks:
            return
        t, func, args = self.tasks[uid]
        if args is None:
            func()
        else:
            func(*args)
        self.tasks.pop(uid)

    # 获取当前时间
    def time(self) -> Time:
        cur = time.time()
        time_pass = cur - self.system_base_time
        return Time(self.base_time + time_pass * self.ratio)

    # 创建定时任务
    def create_task(self, interval, callback, args = None):
        interval = interval / self.ratio
        uid = self.__task_id()
        t = threading.Timer(interval, self.__callback, args = (uid,))
        self.tasks[uid] = (t, callback, (args,))
        t.start()
        return uid
    
    # 创建定时任务
    def create_task_at(self, time:Time, callback, args = None):
        interval = time - self.time()
        return self.create_task(interval, callback, args)

    # 取消定时任务
    def cancel_task(self, task_id, run = False):
        if task_id in self.tasks:
            t, func, args = self.tasks.pop(task_id)
            t.cancel()
            if run:
                if args is None:
                    func()
                else:
                    func(*args)
            

timer = Timer(SYSTEM_TIME_RATIO)

# example
# if __name__ == "__main__":
#     print(timer.time().to_string())
#     uid = timer.create_task(40, lambda x: print(f'task: {timer.time().to_string()}'))
#     time.sleep(1)
#     timer.cancel_task(uid,True)
#     print(timer.time().to_string())