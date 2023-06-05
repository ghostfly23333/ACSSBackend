import csv
import re
import json
import time as time_
from datetime import date
import threading
import requests


def extract_events(event_str):
    events = []
    pattern = re.compile(r'\((.*?)\)')  # 匹配括号内的内容

    # 使用正则表达式提取括号内的事件
    matches = re.findall(pattern, event_str)
    for match in matches:
        event = match.split(',')
        events.append(tuple(event))

    return events


# def extract_val(data):
#     result = []
#     for item in data:
#         my_list = list(item)
#         print(my_list)


#         #extracted_values = [value.split("'")[1] for value in item if "'" in value]
#         #print(extracted_values)
#         result.append(my_list,)

#     print(result)

'''
    读取 CSV 文件
'''
event_list = []
# 获取今天的日期
current_date = date.today()
date_string = current_date.strftime("%Y-%m-%d")
# 打开 CSV 文件
with open('4a.csv', 'r') as file:
    # 创建 CSV 读取器
    reader = csv.reader(file)

    # 遍历每一行数据
    for row in reader:
        # 忽略空行
        if not any(row):
            continue

        # 提取时间和事件数据
        time = time_.mktime(time_.strptime(date_string+" "+row[0], "%Y-%m-%d %H:%M:%S"))
        events = []

        # 处理事件数据
        if len(row) > 1:
            event_str = row[1].strip()

            # 提取事件
            events = extract_events(event_str)
        event_list.append((time, events))
'''
    生成 JSON 请求
'''
for item in event_list:
    print(item)
file = open('output.txt', 'w')

time_url = "http://127.0.0.1:10443/time"
headers = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
}
time_payload = json.dumps({
    })


def print_result():
    test_url = 'http://127.0.0.1:10443/result'
    test_payload = json.dumps({
        })
        
    response = requests.request("POST", test_url, headers=headers, data=test_payload)
    print(response.text.encode('utf8').decode('unicode_escape'), file=file)


while(1):
    if len(event_list) == 0:
        break
    response = requests.request("GET", time_url, headers=headers, data=time_payload)
    now_stamp = json.loads(response.text)['data']['stamp']
   # print(now_stamp)

    url = ""
    payload = json.dumps({})
    event_time = event_list[0][0]
    if event_time - now_stamp < 5:
        # 事件已经发生
        for item in event_list[0][1]:
            if item[0] == 'A':
                # 提交充电申请
                if item[3] == '0':
                    # 取消充电
                    url = "http://127.0.0.1:10443/user/alter/cancel"
                    payload = json.dumps({
                        "user_id": "user1",
                        "car_id": item[1],
                    })
                else:
                    # 正常提交充电请求
                    mode = 1 if item[2] == 'F' else 0
                    url = "http://127.0.0.1:10443/user/charge"
                    payload = json.dumps({
                        "user_id": "user1",
                        "car_id": item[1],
                        "mode": mode,
                        "amount": float(item[3])
                    })
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text.encode('utf8').decode('unicode_escape'),file=file)
            elif item[0] == 'B':
                # 充电桩故障
                url = 'http://127.0.0.1:10443/admin/alter/pile'
                status = 2 if item[3] == '0' else 1
                payload = json.dumps({
                    "pile_id": item[1],
                    "status": status,
                })
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text.encode('utf8').decode('unicode_escape'),file=file)
            else:
                # 变更充电请求
                if item[3] == '-1':
                    # 充电量不变 更改充电模式
                    url = 'http://127.0.0.1:10443/user/alter/mode'
                    mode = 1 if item[2] == 'F' else 0
                    payload = json.dumps({
                        "user_id": "user1",
                        "car_id": item[1],
                        "mode": mode
                    })
                elif item[2] == 'O':
                    # 充电量变更
                    url = 'http://127.0.0.1:10443/user/alter/amount'
                    payload = json.dumps({
                        "user_id": "user1",
                        "car_id": item[1],
                        "amount": float(item[3])
                    })
                else:
                    # 充电量和充电模式都变更
                    url = 'http://127.0.0.1:10443/user/alter/mode_and_amount'
                    mode = 1 if item[2] == 'F' else 0
                    payload = json.dumps({
                        "user_id": "user1",
                        "car_id": item[1],
                        "mode": mode,
                        "amount": float(item[3])
                    })
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text.encode('utf8').decode('unicode_escape'), file=file)
            # print(key, value)
            formatted_time = time_.strftime("%Y-%m-%d %H:%M:%S", time_.localtime(event_time))
            print(time_.strftime("%Y-%m-%d %H:%M:%S", time_.localtime(event_time)), file=file)
            print(time_.strftime("%Y-%m-%d %H:%M:%S", time_.localtime(now_stamp)), file=file)
            print(url, payload, file=file)
        file.flush()
        event_list.pop(0)
        threading.Timer(1,print_result).start()
        
    time_.sleep(0.2)


