# 各充电桩的当前状态信息（是否正常工作、系统启动后累计充电次数、充电总时长、充电总电量

def get_charging_piles_status(charging_piles):
    status = []
    for pile in charging_piles:
        # 模拟获取充电桩状态信息的过程，这里简单地返回一些随机数据
        working_status = pile.working_status
        total_charges = pile.total_charges
        total_time = pile.charge_time
        total_energy = pile.charge_amount

        status.append({
            "pile_id": pile.pile_id,
            "status": working_status,
            "amount": total_energy,
            "time": total_time,
            "total_charges": total_charges,
        })
    return status