from configs import input_file_name
import pandas as pd


def transform_df_to_dict_equipment(eq) -> dict:
    # df --> {'equip_1111': 'mode_0',       -->  {1111: 0,
    #         'equip_2111': 'mode_1', ...}        2111: 1, ...}
    columns = list(eq)
    eq = eq.set_index(columns[0]).T.to_dict('list')
    eq = {eq_id: eq_mode[0] for eq_id, eq_mode in eq.items()}
    return {int(eq_id): int(eq_mode) for key, value in eq.items() for eq_id in key.split('_')
            for eq_mode in value.split('_') if eq_id.isdigit() and eq_mode.isdigit()}


def transform_df_to_dict_subproduct(subpr) -> dict:
    #       {'subproduct_111': {'equip_1111': {'duration, min': 10, 'unit': 'kg'}},          {111: {1111: {'duration, min': 10, 'unit': 'kg'}},
    # df --> 'subproduct_211': {'equip_2111': {'duration, min': 15, 'unit': 'kg'},       -->  211: {2111: {'duration, min': 15, 'unit': 'kg'},
    #                          {'equip_2112': {'duration, min': 25, 'unit': 'kg'}}, ...}           {2112: {'duration, min': 25, 'unit': 'kg'}}, ...}
    columns = list(subpr)
    subpr = subpr.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()
    res = {int(subpr_id): value for key, value in subpr.items() for subpr_id in key.split('_') if subpr_id.isdigit()}
    for key, value in res.items():
        res[key] = {int(eq_id): info for eq_ids, info in value.items() for eq_id in eq_ids.split('_') if eq_id.isdigit()}

    # for key, value in res.items():
    #     for suborder, info in value.items():
    #         info['duration, min'] += 400

    return res


def transform_df_to_dict_switch_time(sw_time) -> dict:
    #       {'subproduct_111': {'equip_1111': 120,          {111: {1111: 120,
    # df -->                    'equip_1112': 50},      -->        1112: 50},
    #        'subproduct_211': {'equip_2111': 90}, ...}      211: {2111: 90}, ...}
    columns = list(sw_time)
    columns = columns[1:2] + columns[:1] + columns[2:]
    sw_time = sw_time.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()
    for subpr_id, info in sw_time.items():
        sw_time[subpr_id] = {eq_id: duration for eq_id, value in info.items() for key, duration in value.items()}
    res = {int(subpr_id): value for key, value in sw_time.items() for subpr_id in key.split('_') if subpr_id.isdigit()}
    for key, value in res.items():
        res[key] = {int(eq_id): info for eq_ids, info in value.items() for eq_id in eq_ids.split('_') if eq_id.isdigit()}
    return res


def transform_df_to_dict_orders(ords) -> dict:
    #       {'order_1': {'suborder_11': {'quantity': 200, 'unit': 'kg', 'price': 1011}},
    # df --> 'order_2': {'suborder_21': {'quantity': 120, 'unit': 'kg', 'price': 4500},        -->
    #                    'suborder_22': {'quantity': 230, 'unit': 'kg', 'price': 4500}}, ...}
    #          {1: {11: {'quantity': 200, 'unit': 'kg', 'price': 1011}},
    #    -->    2: {21: {'quantity': 120, 'unit': 'kg', 'price': 4500},
    #               22: {'quantity': 230, 'unit': 'kg', 'price': 4500}}, ...}
    columns = list(ords)
    ords = ords.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[-1]).to_dict('index')).to_dict()
    res = {int(ord_id): value for key, value in ords.items() for ord_id in key.split('_') if ord_id.isdigit()}
    for key, value in res.items():
        res[key] = {int(subord_id): info for subord_ids, info in value.items() for subord_id in subord_ids.split('_') if subord_id.isdigit()}
    return res


def transform_df_to_dict_structure(struct) -> dict:
    #        {'order_1': {'suborder_11': 'subproduct_111',           {1: {11: 111,
    # df -->              'suborder_12': 'subproduct_112'},      -->      12: 112},
    #         'order_2': {'suborder_22': 'subproduct_211'}, ...}      2: {22: 211}, ...}
    columns = list(struct)
    struct = struct.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()
    for order_id, info in struct.items():
        struct[order_id] = {suborder_id: subprod_id for suborder_id, value in info.items() for key, subprod_id in value.items()}
    res = {int(ord_id): value for key, value in struct.items() for ord_id in key.split('_') if ord_id.isdigit()}
    for key, value in res.items():
        res[key] = {int(subord_id): int(subprod_id) for subord_ids, subprod_ids in value.items()
                    for subord_id in subord_ids.split('_') for subprod_id in subprod_ids.split('_') if subord_id.isdigit() and subprod_id.isdigit()}
    return res


def transform_df_to_dict_order_graph(ord_gr) -> dict:
    # df --> {'suborder_10': ['suborder_12', 'suborder_13'], --> {10: [12, 13],
    #         'suborder_12': ['suborder_24'], ...}                12: [24], ...}
    columns = list(ord_gr)
    ord_gr = ord_gr.groupby(columns[0])[columns[1]].apply(list).to_dict()
    res = {int(subord_id): value for key, value in ord_gr.items() for subord_id in key.split('_') if subord_id.isdigit()}
    for key, value in res.items():
        new_value = []
        for subord_ids in value:
            for el in subord_ids.split('_'):
                if el.isdigit():
                    new_value.append(int(el))
        res[key] = new_value
    return res


def transform_df_to_dict_movement_time(move_time) -> dict:
    #        {'subproduct_111': {('equip_1111', 'equip_2112'): 1440,           {111: {(1111, 2112): 1440,
    # df -->                     ('equip_2453', 'equip_1457'): 1680},     -->         (2453, 1457): 1680},
    #         'subproduct_211': {('equip_2111', 'equip_3612'): 1520}, ...}      211: {(2111, 3612): 1520}, ...}
    columns = list(move_time)
    columns = columns[-2:-1] + columns[:-2] + columns[-1:]
    move_time = move_time.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index([columns[1], columns[2]]).to_dict('index')).to_dict()
    for subprod_id, info in move_time.items():
        move_time[subprod_id] = {path: duration for path, value in info.items() for key, duration in value.items()}
    move_time = {int(subprod_id): value for key, value in move_time.items() for subprod_id in key.split('_') if subprod_id.isdigit()}
    res = {}
    for subprod_id, info in move_time.items():
        new_info = {}
        for key, value in info.items():
            path = []
            for eq_ids in key:
                for el in eq_ids.split('_'):
                    if el.isdigit():
                        path.append(int(el))
            new_info[tuple(path)] = value
        res[subprod_id] = new_info
    return res


class Reader:

    def __init__(self):
        # reading info from the lists
        self.equipment = pd.read_excel(input_file_name, sheet_name='equipment').iloc[:, 1:]
        self.subproduct = pd.read_excel(input_file_name, sheet_name='subproduct').iloc[:, 1:]
        self.switch_time = pd.read_excel(input_file_name, sheet_name='switch_time').iloc[:, 1:]
        self.orders = pd.read_excel(input_file_name, sheet_name='orders').iloc[:, 1:]
        self.structure = pd.read_excel(input_file_name, sheet_name='structure').iloc[:, 1:]
        self.order_graph = pd.read_excel(input_file_name, sheet_name='order_graph').iloc[:, 1:]
        self.movement_time = pd.read_excel(input_file_name, sheet_name='movement_time').iloc[:, 1:]

    def transform_df_to_dict(self):
        self.equipment = transform_df_to_dict_equipment(self.equipment)
        self.subproduct = transform_df_to_dict_subproduct(self.subproduct)
        self.switch_time = transform_df_to_dict_switch_time(self.switch_time)
        self.orders = transform_df_to_dict_orders(self.orders)
        self.structure = transform_df_to_dict_structure(self.structure)
        self.order_graph = transform_df_to_dict_order_graph(self.order_graph)
        self.movement_time = transform_df_to_dict_movement_time(self.movement_time)
        return self.equipment, self.subproduct, self.switch_time, self.orders,\
               self.structure, self.order_graph, self.movement_time


if __name__ == '__main__':
    reader = Reader()
    reader.transform_df_to_dict()
    print(reader.switch_time)
