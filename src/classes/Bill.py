class Bill:
    def __init__(self):
        
        self.content = {
            'bill_id':None,
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
    
    def fill(self,bill_id:str,
                date:str,
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
            'bill_id':bill_id,
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
    def generate_request(self,bill_id,date,pile,car,mode,start_time):
        self.fill(bill_id,date,pile,car,mode,0,0,start_time,None,0,0,0)        
        return self
    

    # todo：计算时间
    # def divide_into_period(start_time,cur_time):
        
    # 拿取信息计算价格
    def compute_price(self,cur_time):
        cur_duration,peak,shoulder,off_peak=self.divide_into_period(self['start_time'],cur_time)
        if(self['mode']==0):#常规
           power=7
        else:
            power=30
        kw_h_p=peak/power
        kw_h_s=shoulder/power
        kw_h_o=off_peak/power
        
        cur_amount = kw_h_p + kw_h_s+ kw_h_o
        cur_service = 0.8*cur_amount
        cur_charge = 1*kw_h_p+0.7*kw_h_s+0.4*kw_h_o
        return cur_duration,cur_amount,cur_service,cur_charge
        
    # 仍在充电时，若有实时查找需求，填入具体值，返回表单引用
    def real_time_generate(self,cur_time):
        cur_duration,cur_amount,cur_service,cur_charge=self.compute_price(cur_time)
        self['end_time']=cur_time
        self['amount'] = cur_amount
        self['duration']=cur_duration
        self['service_cost']=cur_service
        self['charge']=cur_charge
        self['total']=cur_service+cur_charge
        return self
    
    # 充电结束后，生成一份静态报表，存进容器
    def persist(self,end_time,container):
        self.real_time_generate(end_time)
        container.insert(self)
        
    
    
class BillContainer:
    container: dict
    
    def __init__(self):
        self.container=dict()
    
    def __str__(self):
        return self.container.__str__()
    
    def insert(self,bill):
        self.container[bill['bill_id']]=bill
    
    def find(self,bill_id):
        return self.container[bill_id]
    
    def delete(self,bill_id):
        self.container.pop(bill_id)
    
    def update(self,bill):
        self.container[bill['bill_id']]=bill

    def find_value(self,param,argument):
        for i in self.container.values():
            # print(i)
            if i[param]==argument:
                return i
        return ValueError

    def find_value_multi(self,param,argument):
        result = []
        for i in self.container.items():
            # print(i)
            if i[1][param]==argument:
                result.append(i[1])
        return result
                    
    # todo: 充电结束后，有查找需求，在容器内查找静态报表
    
                    
# con = BillContainer()

# a = Bill('1','1',2,'3','0',5,5,'day1','day2',100,100)
# print(a)
# con.insert(a)
# # print(con)
# print(con.find_value('start_time','day1'))