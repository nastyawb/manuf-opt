from utils.data_reader import Reader


class Data:

    def __init__(self):
        self.reader = Reader()
        self.equip, self.subprod, self.switch_time, self.orders, self.structure, \
        self.order_graph, self.movement_time = self.reader.transform_df_to_dict()

        self.suborder_subproduct_map = self.get_suborder_subprod_map()
        self.final_suborders_id = self.get_final_suborders_id()
        self.to_suborders = [x for sublist in self.order_graph.values() for x in sublist]
        self.relevant_suborder_id, self.relevant_order_graph = self.get_relevant_suborder_id_and_graph()
        self.relevant_subprod_id = self.get_relevant_subprod_id()
        self.relevant_equip_id, self.relevant_subprod = self.get_relevant_equip_id_and_subprod_info()
        self.relevant_switch_time = self.get_relevant_switch_time()
        self.relevant_equip = self.get_relevant_equip_info()
        self.relevant_movement_time = self.get_relevant_movement_time()

    def get_final_suborders_id(self):
        final_suborders_id = []
        for order_id, order_info in self.orders.items():
            for suborder_id, info in order_info.items():
                final_suborders_id.append(suborder_id)
        return final_suborders_id

    def get_suborder_subprod_map(self):
        suborder_subproduct_map = {}
        for order_id, info in self.structure.items():
            for subord_id, subprod_id in info.items():
                suborder_subproduct_map[subord_id] = subprod_id
        return suborder_subproduct_map

    def get_relevant_suborder_id_and_graph(self):
        relevant_order_graph = {}
        relevant_suborder_id = [x for x in self.final_suborders_id]
        for curr_suborder in relevant_suborder_id:
            if curr_suborder in self.to_suborders:
                for from_s, to_s in self.order_graph.items():
                    if curr_suborder in to_s and from_s not in relevant_suborder_id:
                        relevant_suborder_id.append(from_s)
                        relevant_order_graph[from_s] = to_s
        return relevant_suborder_id, relevant_order_graph

    def get_relevant_subprod_id(self):
        relevant_subprod_id = [subprod_id for suborder_id, subprod_id in self.suborder_subproduct_map.items()
                               if suborder_id in self.relevant_suborder_id]
        return list(dict.fromkeys(relevant_subprod_id))

    def get_relevant_equip_id_and_subprod_info(self):
        relevant_equip_id = []
        relevant_subprod_info = {}
        for subprod_id, info in self.subprod.items():
            if subprod_id in self.relevant_subprod_id:
                relevant_subprod_info[subprod_id] = self.subprod[subprod_id]
                for equip_id, time in info.items():
                    if equip_id not in relevant_equip_id:
                        relevant_equip_id.append(equip_id)
        return relevant_equip_id, relevant_subprod_info

    def get_relevant_equip_info(self):
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
        for subprod_id in self.relevant_subprod_id:
            for equip_id in self.relevant_equip_id:
                if subprod_id not in relevant_switch_time.keys() or (equip_id not in relevant_switch_time[subprod_id].keys()
                                                                     and equip_id in self.subprod[subprod_id].keys()):
                    relevant_switch_time[subprod_id] = {equip_id: 1000}
        for subprod_id, subprod_info in self.subprod.items():
            for equip_id in subprod_info.keys():
                for s_id, sw_info in relevant_switch_time.items():
                    if equip_id not in sw_info.keys() and s_id == subprod_id and self.equip[equip_id] == 1:
                        relevant_switch_time[s_id][equip_id] = 0
        return relevant_switch_time

    def get_relevant_movement_time(self):
        relevant_movement_time = {}
        for subprod_id, info in self.movement_time.items():
            if subprod_id in self.relevant_subprod_id:
                relevant_movement_time[subprod_id] = {(eq_i, eq_j): duration for (eq_i, eq_j), duration in info.items()
                                                      if eq_i in self.relevant_equip_id and eq_j in self.relevant_equip_id and eq_i != eq_j}
        for subprod_id in self.relevant_subprod_id:
            if subprod_id not in relevant_movement_time.keys():
                relevant_movement_time[subprod_id] = {(equip_1, equip_2): 1000 for equip_1 in self.relevant_equip_id
                                                      for equip_2 in self.relevant_equip_id if equip_1 != equip_2}
        for subprod_id in relevant_movement_time.keys():
            relevant_movement_time[subprod_id] = {(equip_1, equip_2): 1000 for equip_1 in self.relevant_equip_id for equip_2 in self.relevant_equip_id}
        return relevant_movement_time


if __name__ == '__main__':
    data = Data()
    print(data.relevant_equip_id)
    print(data.relevant_subprod_id)
    print(data.relevant_switch_time[1641])
    # print(sorted(data.relevant_suborder_id))
    # print(data.relevant_order_graph)
    # print(sorted(data.relevant_subprod_id))
    # print(sorted(data.relevant_equip_id))
    # print(data.relevant_subprod)
    # print(data.relevant_switch_time)
    # print(data.relevant_equip)
    # print(data.relevant_movement_time)
