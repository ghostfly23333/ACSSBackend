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
            'total':total,
            }
    
    # todo：仍在充电时，若有查找需求，生成一个实例，不插入容器
    def generate_request(self,bill_id,date,pile,car,mode,start_time):
        
    
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
        
    # def print(self):
    #     print(self.container)

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
                    
    
    # todo: 充电结束后，生成一份静态报表，存进容器
    # todo: 充电结束后，有查找需求，在容器内查找静态报表
                    
# con = BillContainer()

# a = Bill('1','1',2,'3','0',5,5,'day1','day2',100,100)
# print(a)
# con.insert(a)
# # print(con)
# print(con.find_value('start_time','day1'))