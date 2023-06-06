import time
import threading
from config.sys import SYSTEM_TIME_RATIO,SYSTEM_TIME_START


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
    
    def to_dict(self) -> dict:
        return {
            "stamp": self.stamp,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second
        }
    
    def __sub__(self, other) -> float:
        return abs(self.stamp - other.stamp)
    

class Timer:
    _system__base_time : float
    _base_time : float
    _task_id: int
    _lock = threading.Lock()
    _dict_lock = threading.Lock()
    _tasks : dict
    _ratio : int
    # 初始化
    def __init__(self, _ratio:int = 1, base:Time = None) -> None:
        self._system__base_time = time.time()
        if base is None:
            self._base_time = self._system__base_time
        else:
            self._base_time = base.stamp

        self._ratio = _ratio
        self._task_id = 0
        self._tasks = {}
    
    # 任务id
    def __task_id__(self):
        with self._lock:
            self._task_id += 1
            return self._task_id

    # 定时任务回调
    def __callback__(self, uid):
        if uid not in self._tasks:
            return
        t, func, args = self._tasks[uid]
        if args is None:
            func()
        else:
            func(*args)
        self._tasks.pop(uid)

    # 获取当前时间
    def time(self) -> Time:
        cur = time.time()
        time_pass = cur - self._system__base_time
        return Time(self._base_time + time_pass * self._ratio)
    
    def time_in_day(self,hour,minute,second = 0):
        cur = self.time()
        return Time.make(f'{cur.year}-{cur.month}-{cur.day} {hour}:{minute}:{second}')


    # 创建定时任务
    def create_task(self, interval, callback, args = None):
        interval = interval / self._ratio
        uid = self.__task_id__()
        t = threading.Timer(interval, self.__callback__, args = (uid,))
        self._tasks[uid] = (t, callback, args)
        t.start()
        return uid
    
    # 创建定时任务
    def create_task_at(self, time:Time, callback, args = None):
        interval = time - self.time()
        return self.create_task(interval, callback, args)

    # 取消定时任务
    def cancel_task(self, _task_id, run = False):
        if _task_id in self._tasks:
            t, func, args = self._tasks.pop(_task_id)
            t.cancel()
            if run:
                if args is None:
                    func()
                else:
                    func(*args)
            
if SYSTEM_TIME_START == "":
    timer = Timer(SYSTEM_TIME_RATIO)
else:
    timer = Timer(SYSTEM_TIME_RATIO,Time.make(SYSTEM_TIME_START))

# example
# if __name__ == "__main__":
#     print(timer.time().to_string())
#     uid = timer.create_task(40, lambda x: print(f'task: {timer.time().to_string()}'))
#     time.sleep(1)
#     timer.cancel_task(uid,True)
#     print(timer.time().to_string())