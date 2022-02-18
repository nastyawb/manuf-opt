from configs import input_file_name
import pandas as pd


def transform_df_to_dict_equipment(eq) -> dict:
    # {'equip_1111': 'mode_0',
    #  'equip_2111': 'mode_1', ...}
    columns = list(eq)
    eq = eq.set_index(columns[0]).T.to_dict('list')
    return {eq_id: eq_mode[0] for eq_id, eq_mode in eq.items()}


def transform_df_to_dict_subproduct(subpr) -> dict:
    # {'subproduct_111': {'equip_1111': {'duration, min': 10, 'unit': 'kg'}},
    #  'subproduct_211': {'equip_2111': {'duration, min': 15, 'unit': 'kg'},
    #                    {'equip_2112': {'duration, min': 25, 'unit': 'kg'}}, ...}
    columns = list(subpr)
    return subpr.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()


def transform_df_to_dict_switch_time(sw_time) -> dict:
    # {'subproduct_111': {'equip_1111': 120,
    #                     'equip_1112': 50},
    #  'subproduct_211': {'equip_2111': 90}, ...}
    columns = list(sw_time)
    columns = columns[1:2] + columns[:1] + columns[2:]
    sw_time = sw_time.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()
    for subpr_id, info in sw_time.items():
        sw_time[subpr_id] = {eq_id: duration for eq_id, value in info.items() for key, duration in value.items()}
    return sw_time


def transform_df_to_dict_orders(ords) -> dict:
    # {'order_1': {'suborder_11': {'quantity': 200, 'unit': 'kg', 'price': 1011}},
    #  'order_2': {'suborder_21': {'quantity': 120, 'unit': 'kg', 'price': 4500},
    #              'suborder_22': {'quantity': 230, 'unit': 'kg', 'price': 4500}}, ...}
    columns = list(ords)
    return ords.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[-1]).to_dict('index')).to_dict()


def transform_df_to_dict_structure(struct) -> dict:
    # {'order_1': {'suborder_11': 'subproduct_111',
    #              'suborder_12': 'subproduct_112'},
    #  'order_2': {'suborder_22': 'subproduct_211'}, ...}
    columns = list(struct)
    struct = struct.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index(columns[1]).to_dict('index')).to_dict()
    for order_id, info in struct.items():
        struct[order_id] = {suborder_id: subprod_id for suborder_id, value in info.items() for key, subprod_id in value.items()}
    return struct


def transform_df_to_dict_order_graph(ord_gr) -> dict:
    # {'suborder_10': ['suborder_12', 'suborder_13'],
    #  'suborder_12': ['suborder_24'], ...}
    columns = list(ord_gr)
    return ord_gr.groupby(columns[0])[columns[1]].apply(list).to_dict()


def transform_df_to_dict_movement_time(move_time) -> dict:
    # {'subproduct_111': {('equip_1111', 'equip_2112'): 1440,
    #                     ('equip_2453', 'equip_1457'): 1680,},
    #  'subproduct_211': {('equip_2111', 'equip_3612'): 1520}, ...}
    columns = list(move_time)
    columns = columns[-2:-1] + columns[:-2] + columns[-1:]
    move_time = move_time.groupby(columns[0])[columns[1:]].apply(lambda x: x.set_index([columns[1], columns[2]]).to_dict('index')).to_dict()
    for subprod_id, info in move_time.items():
        move_time[subprod_id] = {path: duration for path, value in info.items() for key, duration in value.items()}
    return move_time


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


if __name__ == '__main__':
    reader = Reader()
    reader.transform_df_to_dict()
    print(reader.movement_time)
