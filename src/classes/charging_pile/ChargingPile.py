class ChargingPile:
    def __init__(self, pile_id, num_ports):
        self.pile_id = pile_id
        self.num_ports = num_ports
        self.ports = [None] * num_ports  
        self.status = 1 # 1: working, 0: not working
        self.charge_amount = 0 # total amount of energy
        self.charge_time = 0 # total time of charging
        

    def __str__(self):
        return f"Charging pile {self.pile_id}: {self.num_ports} ports with {self.status} status"