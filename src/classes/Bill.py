from classes.Timer import timer, Time
from config.sys import PILE_NORMAL_SPEED,PILE_FAST_SPEED,EXPENSE_OFF_PEEK,EXPENSE_PEEK,EXPENSE_REGULAR,EXPENSE_SERVICE
from config.sys import TEST_DATASET

# 划分时间段
def slice_time(start_time,cur_time,period_Start,period_end,period_attr):
    peak,shoulder,off_peak=0,0,0
    duration_h = (cur_time -start_time)/3600

    if start_time.hour in range(period_Start,period_end):
        if cur_time.hour in range(period_Start,period_end):
            if period_attr == 0:#peak
                peak+=duration_h
            elif period_attr == 1:#shoulder
                shoulder+=duration_h
            else :#offpeak
                off_peak+=duration_h
            return start_time,peak,shoulder,off_peak
        
        tmp_time = timer.time_in_day(period_end,0,0)

        if period_attr == 0:#peak
            peak+=(tmp_time - start_time)/3600

        elif period_attr == 1:#shoulder
            shoulder+=(tmp_time - start_time)/3600
        else :#offpeak
            off_peak+=(tmp_time - start_time)/3600
        # start_time = tmp_time
        return tmp_time,peak,shoulder,off_peak
    else:
        return start_time,0,0,0

def divide_into_period(start_time,cur_time):
    duration = cur_time - start_time
    duration_h = duration/3600
    peak,shoulder,off_peak=0,0,0
    if start_time.day == cur_time.day:
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,0,7,2)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,7,10,1)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,10,15,0)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,15,18,1)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,18,21,0)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,21,23,1)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc

        start_time,peak_inc,shoulder_inc,off_peak_inc= slice_time(start_time,cur_time,23,24,2)
        peak+=peak_inc
        shoulder+=shoulder_inc
        off_peak+=off_peak_inc
        
    return  duration_h, peak,shoulder,off_peak

# 拿取信息计算价格
def compute_price(start_time,cur_time,mode):
    cur_duration,peak,shoulder,off_peak=divide_into_period(start_time,cur_time)

    if(mode==0):#常规
        power=PILE_NORMAL_SPEED
    else:
        power=PILE_FAST_SPEED
    kw_h_p=peak*power
    kw_h_s=shoulder*power
    kw_h_o=off_peak*power
    
    cur_amount = kw_h_p + kw_h_s+ kw_h_o
    cur_service = EXPENSE_SERVICE * cur_amount
    cur_charge = EXPENSE_PEEK * kw_h_p + EXPENSE_REGULAR * kw_h_s + EXPENSE_OFF_PEEK * kw_h_o
    return cur_duration,cur_amount,cur_service,cur_charge

class Bill_status:
    Submitted = 0
    Charging = 1
    # Error = 2  

STATUS_SUBMITED = 0
STATUS_CHARGING = 1
STATUS_FINISHED = 2
STATUS_CANCELED = 3
id_count = 0

class BillDetail:
    id:str
    date:str
    status:int
    pile:str
    mode:str
    start_time:Time
    end_time:Time
    amount:float
    service:float
    charge:float

    def __init__(self):
        self.counter = 0
        self.id = ''
        self.date = ''
        self.status = STATUS_SUBMITED
        self.pile = ''
        self.mode = 0
        self.start_time = None
        self.end_time = None
        self.amount = 0
        self.service = 0
        self.charge = 0
        self.duration = 0


    def to_dict(self):
        return {
            'counter':self.counter,
            'id':self.id,
            'date':self.date,
            'status':self.status,
            'pile':self.pile,
            'mode':self.mode,
            'start_time':self.start_time.to_string() if self.start_time else None,
            'end_time':self.end_time.to_string() if self.end_time else None,
            'duration':self.duration,
            'amount':self.amount,
            'service':self.service,
            'charge':self.charge,
            'total':self.service + self.charge
        }
    
    def dump_txt(self,car_id:str):
        start = self.start_time.to_string() if self.start_time != None else "N/A"
        end = self.end_time.to_string() if self.end_time != None else "N/A"
        txt = f'{car_id}\t{self.counter}\t\t{start}\t\t{self.pile}\t\t\t{self.amount:.2f}\t\t{int(self.duration*3600)}\t\t{start}\t\t{end}\t\t{self.charge:.2f}\t\t\t{self.service:.2f}\t\t\t{(self.service + self.charge):.2f}'
        return txt

    def generate(self,bill_id,mode):
        global id_count
        cur_time = timer.time()
        id = f'{bill_id}_{int(cur_time.stamp * 1000)}'
        date = cur_time.to_string()
        self.counter = id_count
        id_count += 1
        self.id = id
        self.date = date
        self.status = STATUS_SUBMITED
        self.mode = mode
        self.amount = 0
        return self

    def start(self):
        if self.status == STATUS_SUBMITED:
            self.start_time = timer.time()
            self.status = STATUS_CHARGING
        return self
    
    def finish(self):
        if self.status == STATUS_CANCELED or self.status == STATUS_FINISHED:
            return
        if self.status == STATUS_SUBMITED:
            self.status = STATUS_CANCELED
            return

        cur_time = timer.time()
        cur_duration,cur_amount,cur_service,cur_charge=compute_price(self.start_time,cur_time,self.mode)
        self.end_time = cur_time
        self.duration = cur_duration
        self.amount = cur_amount
        self.service = cur_service
        self.charge = cur_charge
        self.status = STATUS_FINISHED
        return self

bill_counter = 0

class Bill:
    counter:int
    id:str
    user:str
    car:str
    date:str
    detail:list

    def __init__(self) -> None:
        self.counter = 0
        self.id = ''
        self.car = ''
        self.detail = list()

    def create(self,user_id:str,car_id:str,mode:int):
        global bill_counter
        self.counter = bill_counter
        bill_counter += 1
        self.user = user_id
        self.car = car_id
        self.id = f'{car_id}_{int(timer.time().stamp*1000)}'
        self.date = timer.time().to_string()
        self.detail = list()
        self.detail.append(BillDetail().generate(self.id,mode))
        return self
    
    def new(self,mode:int):
        self.end()
        self.detail.append(BillDetail().generate(self.id,mode))
        return self
    
    def brief(self):
        data = {
            'id':self.id,
            'car':self.car,
            'date':self.date,
            'status':self.detail[-1].status,
        }
        return data
    
    def statistic(self) -> dict:
        data = {
            'date':self.date,
            'start_time':'',
            'end_time':'',
            'duration':0,
            'amount':0,
            'service':0,
            'charge':0,
            'total':0,
        }
        for detail in self.detail:
            if detail.status == STATUS_FINISHED:
                if data['start_time'] == '' and detail.start_time is not None:
                    data['start_time'] =  detail.start_time.to_string()
                if detail.end_time is not None:
                    data['end_time'] = detail.end_time.to_string()
                data['duration'] += detail.duration
                data['amount'] += detail.amount
                data['service'] += detail.service
                data['charge'] += detail.charge
                data['total'] += detail.service + detail.charge
        return data

    def start(self,pile_id:str,mode:int):
        self.detail[-1].pile = pile_id
        self.detail[-1].mode = mode
        self.detail[-1].start()

    def end(self):
        self.detail[-1].finish()

    def to_dict(self):
        return {
            'id':self.id,
            'user':self.user,
            'car':self.car,
            'detail':[d.to_dict() for d in self.detail]
        }
    
    def dump_txt(self):
        data = self.statistic()
        txt = f'{self.car}\t{self.counter}\t\t{data["start_time"]}\t\t{data["amount"]:.2f}\t\t{int(data["duration"]*3600)}\t\t{data["start_time"]}\t\t{data["end_time"]}\t\t{data["service"]:.2f}\t\t\t{data["charge"]:.2f}\t\t\t{data["total"]:.2f}\t\t'
        for i in range(len(self.detail)):
            txt += f'{self.detail[i].counter}'
            if i < len(self.detail) - 1:
                txt += ','
        return txt
    

class BillManager:
    bills:dict

    def __init__(self) -> None:
        self.bills = dict()

    def generate(self,user_id:str,car_id:str,mode:int) -> Bill:
        bill = Bill().create(user_id,car_id,mode)
        self.bills[bill.id] = bill
        return bill

    def find(self,bill_id:str) -> Bill:
        if bill_id not in self.bills:
            return None
        return self.bills[bill_id]
    
    def find_all(self,user_id:str) -> list:
        return [b for b in self.bills.values() if b.user == user_id and (b.detail[-1].status >= STATUS_FINISHED)]
    
    
    def statistic(self) -> dict:
        data = {
            'start':'',
            'end':'',
            'duration':0,
            'amount':0,
            'service':0,
            'charge':0,
            'total':0,
            'count':0
        }
        for bill in self.bills:
            d = self.bills[bill].statistic()
            data['count'] += 1
            data['duration'] += d['duration']
            data['amount'] += d['amount']
            data['service'] += d['service']
            data['charge'] += d['charge']
            data['total'] += d['total']
        return data
    

    def dump_txt(self):
        bf = open(f'{TEST_DATASET}_bill.txt','w',encoding='utf-8')
        df = open(f'{TEST_DATASET}_detail.txt','w',encoding='utf-8')
        bf.write('车辆编码\t账单编号\t账单生成时间\t充电电量(度)\t充电时长(秒)\t启动时间\t停止时间\t充电费用(元)\t服务费用(元)\t总费用(元)\t详单列表编号\n')
        bf.write('='*170)
        bf.write('\n')
        df.write('车辆编码\t详单编号\t详单生成时间\t充电桩编号\t充电电量(度)\t充电时长(秒)\t启动时间\t停止时间\t充电费用(元)\t服务费用(元)\t总费用(元)\n')
        df.write('='*170)
        df.write('\n')
        for idx in self.bills:
            bill = self.bills[idx]
            if bill.detail[-1].status < STATUS_FINISHED:
                continue
            bf.write(bill.dump_txt() + '\n')
            for detail in bill.detail:
                df.write(detail.dump_txt(bill.car) + '\n')
        bf.close()
        df.close()
        

    
bill_manager = BillManager()

    
          
# class Billd:
#     def __init__(self):
        
#         self.content = {
#             'user_id':None,
#             'bill_id':None,
#             'status':None,
#             'date':None,
#             'pile':None,
#             'car':None,
#             'mode':None,
#             'amount':None,
#             'duration':None,
#             'start_time':None,
#             'end_time':None,
#             'service_cost':None,
#             'charge':None,
#             'total':None,
#             }
    
#     def __getitem__(self, key):
#         return self.content[key]
    
#     def __setitem__(self, key,value):
#         self.content[key]=value
        
#     def __str__(self):
#         return self.content.__str__()
    
#     def fill(self,
#                 user_id:str,
#                 bill_id:str,
#                 date:str,
#                 status:int,
#                 pile:int,
#                 car:str,
#                 mode:int,
#                 amount:float,
#                 duration:float,
#                 start_time:str,
#                 end_time:str,
#                 service_cost:float,
#                 charge:float,
#                 total:float):
        
#         self.content = {
#             'user_id':user_id,
#             'bill_id':bill_id,
#             'status':status,
#             'date':date,
#             'pile':pile,
#             'car':car,
#             'mode':mode,
#             'amount':amount,
#             'duration':duration,
#             'start_time':start_time,
#             'end_time':end_time,
#             'service_cost':service_cost,
#             'charge':charge,
#             'total':total,
#             }
        
#     def to_dict(self):
#         return {
#             'user_id':self['user_id'],
#             'bill_id':self['bill_id'],
#             'status':self['status'],
#             'date':self['date'],
#             'car':self['car'],
#             'detail':{
#                 'pile':self['pile'],
#                 'mode':self['mode'],
#                 'amount':self['amount'],
#                 'duration':self['duration'],
#                 'start_time':Time(self['start_time']).to_string(),
#                 'end_time':Time(self['end_time']).to_string(),
#             },
#             'cost':{
#                 'service':self['service_cost'],
#                 'charge':self['charge'],
#                 'total':self['total'],
#             }
#         }
    
        
#     # 充电刚开始，生成初始表单，填入后返回表单引用
#     def generate_request(self,user_id,pile,car,mode,amount,start_time:Time):
#         # start_time = timer.time()
#         bill_id = f'{user_id}_{int(start_time.stamp * 1000)}'
#         date = '%02d-%02d-%02d' % (start_time.year, start_time.month, start_time.day)
#         self.fill(user_id,bill_id,date,1,pile,car,mode,amount,0,start_time.stamp,None,0,0,0)        
#         return self
                      
#     # # 拿取信息计算价格
#     # def compute_price(self,cur_time):
#     #     cur_duration,peak,shoulder,off_peak=divide_into_period(Time(self['start_time']),cur_time)

#     #     if(self['mode']==0):#常规
#     #        power=7
#     #     else:
#     #         power=30
#     #     kw_h_p=peak*power
#     #     kw_h_s=shoulder*power
#     #     kw_h_o=off_peak*power
        
#     #     cur_amount = kw_h_p + kw_h_s+ kw_h_o
#     #     cur_service = 0.8*cur_amount
#     #     cur_charge = 1*kw_h_p+0.7*kw_h_s+0.4*kw_h_o
#     #     return cur_duration,cur_amount,cur_service,cur_charge
        
#     # 仍在充电时，若有实时查找需求，填入具体值，返回表单引用
#     def real_time_generate(self,cur_time):
#         # cur_time = timer.time()
#         cur_duration,cur_amount,cur_service,cur_charge=compute_price(Time(self['start_time']),cur_time,self['mode'])
#         self['end_time']=cur_time.stamp
#         # self['amount'] = cur_amount
#         self['duration']=cur_duration
#         self['service_cost']=cur_service
#         self['charge']=cur_charge
#         self['total']=cur_service+cur_charge
#         return self
    
#     # 充电结束后，生成一份静态报表，存进容器
#     def persist(self,end_time,status,container):
#         self.real_time_generate(end_time)
#         self['status']=status
#         container.insert(self)
        
    
    
# class BillContainer:
#     container: dict
    
#     def __init__(self):
#         self.container=dict()
    
#     def __str__(self):
#         return self.container.__str__()
    
#     def __getitem__(self, key):
#         return self.container[key]
    
#     def __setitem__(self, key,value):
#         self.container[key]=value

#     def add_user(self,user_id):
#         self.container[user_id]=dict()
    
#     def insert(self,bill):
#         if bill['user_id'] not in self.container.keys():
#             self.container[bill['user_id']]={
#                 bill['bill_id']:bill
#             }
#         else:
#             tmp={
#                 bill['bill_id']:bill
#             }
#             self.container[bill['user_id']].update(tmp)
    
#     def all_bills(self):
#         res = []
#         for i in self.container.values():
#             res.extend(i.values())
#         return res
    
#     def find_user(self,user_id):
#         return self.container.get(user_id)
    
#     def delete_user(self,user_id):
#         self.container.pop(user_id)
    
#     def find_bill(self,bill_id):
#         for i in self.container.values():
#             if bill_id in i.keys():
#                 return i[bill_id]
            
#         return None
    
#     def find_user_bill(self,user_id,bill_id):
#         return self.container.get(user_id).get(bill_id)
            
#     def delete_bill(self,bill_id):
#         for k,i in self.container.items():
#             key = list(i.keys())[0]
#             if key == bill_id:
#                 i.pop(bill_id)
#                 if not i:
#                     self.container.pop(k)
#                 break
        
    
#     def update(self,bill):
#         if bill['user_id'] not in self.container.keys():
#             self.container[bill['user_id']]={
#                 bill['bill_id']:bill
#             }
#         else:
#             tmp={
#                 bill['bill_id']:bill
#             }
#             self.container[bill['user_id']].update(tmp)

#     def find_value(self,param,argument):
#         for i in self.container.values():
#             # print(i)
#             for j in i.values():
#                 if j[param]==argument:
#                     return j
#         return None

#     def find_value_multi(self,param,argument):
#         result = []
#         flag = 0
#         for k,v in self.container.items():
#             # print(i)
#             # if i[1][param]==argument:
#             #     result.append(i[1])
#             for j in v.values():
#                 # print(j)
#                 if j[param]==argument:
#                     result.append(j)
#                     flag=1
            
#         return result if flag else None
                    
#     # todo: 充电结束后，有查找需求，在容器内查找静态报表
    
                    
# # con = BillContainer()
# # a = Bill()

# # # print(a)
# # t1=timer.time()
# # a.generate_request('jxf',1,'1',1,t1)
# # t2=Time(t1.stamp+12000)
# # print(t1)
# # print(t2)
# # a.real_time_generate(t2)
# # print(a)
# # t2=Time(t1.stamp+13000)
# # a.persist(t2,0,con)
# # print(a)
# # print()
# # print(jsonify(con.find_user_bill('jxf','1')))