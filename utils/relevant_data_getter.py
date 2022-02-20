from utils.data_reader import Reader


class Data:

    def __init__(self):
        self.reader = Reader()
        self.equip, self.subprod, self.switch_time, self.orders, self.structure, \
        self.order_graph, self.movement_time = self.reader.transform_df_to_dict()

        self.suborder_subproduct_map, self.relevant_subprod_id = self.get_relevant_suborder_info()
        self.relevant_subprod, self.relevant_equip_id = self.get_relevant_subprod_and_equip_id()
        self.relevant_equip = self.get_relevant_equip()
        self.relevant_switch_time = self.get_relevant_switch_time()
        self.relevant_movement_time = self.get_relevant_movement_time()

    def get_relevant_suborder_info(self):
        suborder_subproduct_map = {}
        relevant_subprod_id = []
        for order_id, info in self.structure.items():
            for subord_id, subprod_id in info.items():
                suborder_subproduct_map[subord_id] = subprod_id
                if not subprod_id in relevant_subprod_id:
                    relevant_subprod_id.append(subprod_id)
        return suborder_subproduct_map, sorted(relevant_subprod_id)

    def get_relevant_subprod_and_equip_id(self):
        relevant_subprod = {}
        relevant_equip_id = []
        for subprod_id in self.relevant_subprod_id:
            if subprod_id in self.subprod.keys():
                relevant_subprod[subprod_id] = self.subprod[subprod_id]
                for equip_id, info in self.subprod[subprod_id].items():
                    if not equip_id in relevant_equip_id:
                        relevant_equip_id.append(equip_id)
        return relevant_subprod, sorted(relevant_equip_id)

    def get_relevant_equip(self):
        relevant_equip = {}
        for equip_id, mode in self.equip.items():
            if equip_id in self.relevant_equip_id:
                relevant_equip[equip_id] = mode
        return relevant_equip

    def get_relevant_switch_time(self):
        relevant_switch_time = {}
        for subprod_id, info in self.switch_time.items():
            if subprod_id in self.relevant_subprod_id:
                relevant_switch_time[subprod_id] = {equip_id: duration for equip_id, duration in info.items() if equip_id in self.relevant_equip_id}
        return relevant_switch_time

    def get_relevant_movement_time(self):
        relevant_movement_time = {}
        for subprod_id, info in self.movement_time.items():
            if subprod_id in self.relevant_subprod_id:
                relevant_movement_time[subprod_id] = {(eq_i, eq_j): duration for (eq_i, eq_j), duration in info.items()
                                                      if eq_i in self.relevant_equip_id and eq_j in self.relevant_equip_id and eq_i != eq_j}
        return relevant_movement_time


# if __name__ == '__main__':
#     data = Data()
#     print(data.movement_time)
#     print(data.relevant_movement_time)

