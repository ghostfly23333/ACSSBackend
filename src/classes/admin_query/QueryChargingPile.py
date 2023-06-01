

def get_charging_piles_status(charging_piles):
    status = []
    for pile in charging_piles:
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
