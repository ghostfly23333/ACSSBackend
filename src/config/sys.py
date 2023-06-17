
from enum import Enum


PILE_FAST_SPEED = 30.0      # 快充速度
PILE_NORMAL_SPEED = 7.0     # 慢充速度

EXPENSE_PEEK = 1            # 高峰费率
EXPENSE_REGULAR = 0.7       # 平峰费率
EXPENSE_OFF_PEEK = 0.4      # 谷峰费率
EXPENSE_SERVICE = 0.8       # 服务费率



class ScheduleMode(Enum):
    NORMAL = 0              # 时间顺序调度
    GLOBAL_LIMITED = 1      # 单次调度总充电时长最短
    GLOBAL_IGNORE_MODE = 2  # 批量调度总充电时长最短

SCHEDULE_MODE = ScheduleMode.NORMAL

SYSTEM_TIME_RATIO = 500      # 系统时间倍率
SYSTEM_TIME_START = "2023-06-18 05:55:00"      # 系统时间起始(格式: 2019-01-01 00:00:00, 留空为当前时间)


RUNTIME_HOST = "0.0.0.0"    # 监听地址
RUNTIME_PORT = 10443        # 监听端口
RUNTIME_DEBUG = True        # 调试信息

TEST_DATASET = '4b'          # 测试数据集