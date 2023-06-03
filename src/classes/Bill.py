from Timer import timer
from Timer import Time

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
        power=7
    else:
        power=30
    kw_h_p=peak*power
    kw_h_s=shoulder*power
    kw_h_o=off_peak*power
    
    cur_amount = kw_h_p + kw_h_s+ kw_h_o
    cur_service = 0.8*cur_amount
    cur_charge = 1*kw_h_p+0.7*kw_h_s+0.4*kw_h_o
    return cur_duration,cur_amount,cur_service,cur_charge
        
class Bill:
    def __init__(self):
        
        self.content = {
            'user_id':None,
            'bill_id':None,
            'status':None,
            'date':None,
            'pile':None,
            'car':None,
            'mode':None,
            'amount':None,
            'duration':None,
            'start_time':None,
            'end_time':None,
            'service_cost':None,
            'charge':None,
            'total':None,
            }
    
    def __getitem__(self, key):
        return self.content[key]
    
    def __setitem__(self, key,value):
        self.content[key]=value
        
    def __str__(self):
        return self.content.__str__()
    
    def fill(self,
                user_id:str,
                bill_id:str,
                date:str,
                status:int,
                pile:int,
                car:str,
                mode:int,
                amount:float,
                duration:float,
                start_time:str,
                end_time:str,
                service_cost:float,
                charge:float,
                total:float):
        
        self.content = {
            'user_id':user_id,
            'bill_id':bill_id,
            'status':status,
            'date':date,
            'pile':pile,
            'car':car,
            'mode':mode,
            'amount':amount,
            'duration':duration,
            'start_time':start_time,
            'end_time':end_time,
            'service_cost':service_cost,
            'charge':charge,
            'total':total,
            }
        
    # 充电刚开始，生成初始表单，填入后返回表单引用
    def generate_request(self,user_id,pile,car,mode):
        start_time = timer.time()
        bill_id = user_id +'-'+ str(start_time)
        date = '%02d-%02d-%02d' % (start_time.year, start_time.month, start_time.day)
        self.fill(user_id,bill_id,date,1,pile,car,mode,0,0,start_time.stamp,None,0,0,0)        
        return self
                      
    # # 拿取信息计算价格
    # def compute_price(self,cur_time):
    #     cur_duration,peak,shoulder,off_peak=divide_into_period(Time(self['start_time']),cur_time)

    #     if(self['mode']==0):#常规
    #        power=7
    #     else:
    #         power=30
    #     kw_h_p=peak*power
    #     kw_h_s=shoulder*power
    #     kw_h_o=off_peak*power
        
    #     cur_amount = kw_h_p + kw_h_s+ kw_h_o
    #     cur_service = 0.8*cur_amount
    #     cur_charge = 1*kw_h_p+0.7*kw_h_s+0.4*kw_h_o
    #     return cur_duration,cur_amount,cur_service,cur_charge
        
    # 仍在充电时，若有实时查找需求，填入具体值，返回表单引用
    def real_time_generate(self,cur_time):
        # cur_time = timer.time()
        cur_duration,cur_amount,cur_service,cur_charge=compute_price(Time(self['start_time']),cur_time,self['mode'])
        self['end_time']=cur_time.stamp
        self['amount'] = cur_amount
        self['duration']=cur_duration
        self['service_cost']=cur_service
        self['charge']=cur_charge
        self['total']=cur_service+cur_charge
        return self
    
    # 充电结束后，生成一份静态报表，存进容器
    def persist(self,end_time,status,container):
        self.real_time_generate(end_time)
        self['status']=status
        container.insert(self)
        
    
    
class BillContainer:
    container: dict
    
    def __init__(self):
        self.container=dict()
    
    def __str__(self):
        return self.container.__str__()
    
    def __getitem__(self, key):
        return self.container[key]
    
    def __setitem__(self, key,value):
        self.container[key]=value
    
    def insert(self,bill):
        if bill['user_id'] not in self.container.keys():
            self.container[bill['user_id']]={
                bill['bill_id']:bill
            }
        else:
            tmp={
                bill['bill_id']:bill
            }
            self.container[bill['user_id']].update(tmp)
        
    
    def find_user(self,user_id):
        return self.container.get(user_id)
    
    def delete_user(self,user_id):
        self.container.pop(user_id)
    
    def find_bill(self,bill_id):
        for i in self.container.values():
            if bill_id in i.keys():
                return i[bill_id]
            
        return None
    
    def delete_bill(self,bill_id):
        for k,i in self.container.items():
            key = list(i.keys())[0]
            if key == bill_id:
                i.pop(bill_id)
                if not i:
                    self.container.pop(k)
                break
        
    
    def update(self,bill):
        if bill['user_id'] not in self.container.keys():
            self.container[bill['user_id']]={
                bill['bill_id']:bill
            }
        else:
            tmp={
                bill['bill_id']:bill
            }
            self.container[bill['user_id']].update(tmp)

    def find_value(self,param,argument):
        for i in self.container.values():
            # print(i)
            for j in i.values():
                if j[param]==argument:
                    return j
        return None

    def find_value_multi(self,param,argument):
        result = []
        flag = 0
        for k,v in self.container.items():
            # print(i)
            # if i[1][param]==argument:
            #     result.append(i[1])
            for j in v.values():
                # print(j)
                if j[param]==argument:
                    result.append(j)
                    flag=1
            
        return result if flag else None
                    
    # todo: 充电结束后，有查找需求，在容器内查找静态报表
    
                    
# con = BillContainer()
# a = Bill()
# a.generate_request('jxf',1,'1',1)
# # print(a)
# t1=timer.time()
# t2=Time(t1.stamp+12000)
# print(t1)
# print(t2)
# a.real_time_generate(t2)
# print(a)
# t2=Time(t1.stamp+13000)
# a.persist(t2,0,con)
# print(a)
# print(list(con['jxf'].items())[0][1])