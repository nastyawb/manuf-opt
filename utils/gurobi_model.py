from gurobipy import (GRB,
                      Model,
                      quicksum)
from utils.data_reader import Reader
from utils.relevant_data_getter import Data
from configs import bigM, deadline


class GRBModel:

    def __init__(self):

        self.reader = Reader()
        self.data = Data()

        self.equip = self.data.relevant_equip
        self.subprod = self.data.relevant_subprod
        self.switch_time = self.data.relevant_switch_time
        self.orders = self.data.orders
        self.suborder_subproduct_map = self.data.suborder_subproduct_map
        self.subprod_id = self.data.relevant_subprod_id
        self.final_subord_id = self.data.final_suborders_id
        self.equip_id = self.data.relevant_equip_id
        self.subord_id = self.data.relevant_suborder_id
        self.orders = self.data.orders
        self.order_graph = self.data.order_graph
        self.movement_time = self.data.relevant_movement_time

        self.model = Model('manuf-opt')
        self.eps = {}
        self.b = {}
        self.c = {}
        self.gamma = {}
        self.ksi = {}
        self.delta = {}
        self.obj = 0

    def add_vars(self):
        for subord in self.subord_id:
            self.b[subord] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name=f'b_{subord}')
            self.c[subord] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name=f'c_{subord}')
            for equip in self.equip_id:
                if equip in self.subprod[self.suborder_subproduct_map[subord]].keys():
                    self.eps[subord, equip] = self.model.addVar(vtype=GRB.BINARY, name=f'eps_{subord}_{equip}')

                for to_subord in self.subord_id:
                    for to_equip in self.equip_id:
                        if subord != to_subord and subord in self.order_graph.keys() and to_subord in self.order_graph[subord] \
                                and to_equip in self.subprod[self.suborder_subproduct_map[to_subord]].keys():
                            self.gamma[subord, equip, to_subord, to_equip] = self.model.addVar(vtype=GRB.BINARY,
                                                                                               name=f'gamma_{subord}_{equip}_{to_subord}_{to_equip}')
        for subord in self.final_subord_id:
            self.ksi[subord] = self.model.addVar(vtype=GRB.BINARY, name=f'ksi_{subord}')
        for equip in self.equip_id:
            for from_subord in self.subord_id:
                for to_subord in self.subord_id:
                    if from_subord != to_subord and equip in self.subprod[self.suborder_subproduct_map[from_subord]].keys() \
                            and equip in self.subprod[self.suborder_subproduct_map[to_subord]].keys():
                        self.delta[from_subord, to_subord, equip] = self.model.addVar(vtype=GRB.BINARY,
                                                                                      name=f'delta_{from_subord}_{to_subord}_{equip}')
        # self.mu = self.model.addVars(self.subord_id, self.subord_id, vtype=GRB.BINARY, name='mu')

    def add_subprod_constrs(self):
        for subord in self.subord_id:
            self.model.addConstr((quicksum(self.eps[subord, h] for h in self.subprod[self.suborder_subproduct_map[subord]].keys()) == 1),
                                 name=f'suborder{subord}_can_be_processed_only_once')
            self.model.addConstr(
                self.b[subord] + quicksum(self.eps[subord, h] * self.subprod[self.suborder_subproduct_map[subord]][h]['duration, min']
                                          for h in self.subprod[self.suborder_subproduct_map[subord]].keys()) == self.c[subord],
                name=f'suborder{subord}___start_time_+_processing_time_=_end_time')

    def add_order_constrs(self):
        for from_subord in self.subord_id:
            for to_subord in self.subord_id:
                if from_subord != to_subord and from_subord in self.order_graph.keys() and to_subord in self.order_graph[from_subord]:
                    self.model.addConstr(quicksum(self.gamma[from_subord, h, to_subord, p]
                                                  for h in self.subprod[self.suborder_subproduct_map[from_subord]].keys()
                                                  for p in self.subprod[self.suborder_subproduct_map[to_subord]].keys()) == 1,
                                         name=f'after_suborder{from_subord}_suborder{to_subord}_can_be_processed_only_once')

                    self.model.addConstr(self.c[from_subord] + quicksum(self.gamma[from_subord, h, to_subord, p]
                                                                        * self.movement_time[self.suborder_subproduct_map[from_subord]][(h, p)]
                                                                        for h in self.subprod[self.suborder_subproduct_map[from_subord]].keys()
                                                                        for p in self.subprod[self.suborder_subproduct_map[to_subord]].keys())
                                         + quicksum(self.eps[to_subord, p] * self.switch_time[self.suborder_subproduct_map[to_subord]][p]
                                                    for p in self.subprod[self.suborder_subproduct_map[to_subord]].keys()) <= self.b[to_subord],
                                         name=f'start_subord{to_subord}_=_end_subord{from_subord}_+_move_subord{from_subord}'
                                              f'+_switch_subord{to_subord}')
        for final_subord in self.final_subord_id:
            self.model.addConstr(self.c[final_subord] <= deadline + bigM * (1 - self.ksi[final_subord]),
                                 name=f'final_suborder{final_subord}_processing_finished_before_deadline')

    def add_equip_constrs(self):
        for from_subord in self.subord_id:
            for to_subord in self.subord_id:
                for equip in self.equip_id:
                    if from_subord != to_subord and self.equip[equip] == 0 and equip in self.subprod[self.suborder_subproduct_map[from_subord]].keys() \
                            and equip in self.subprod[self.suborder_subproduct_map[to_subord]].keys():
                        self.model.addConstr(self.c[from_subord]
                                             + self.eps[to_subord, equip] * self.switch_time[self.suborder_subproduct_map[to_subord]][equip]
                                             <= self.b[to_subord] + bigM * self.delta[from_subord, to_subord, equip],
                                             name=f'start_subord{to_subord} = end_subord{from_subord}_+_switch_subord{to_subord}')
                        self.model.addConstr(self.c[to_subord]
                                             + self.eps[from_subord, equip] * self.switch_time[self.suborder_subproduct_map[from_subord]][equip]
                                             <= self.b[from_subord] + bigM * (1 - self.delta[from_subord, to_subord, equip]),
                                             name=f'start_subord{from_subord} = end_subord{to_subord}_+_switch_subord{from_subord}')

    def set_objective_function(self):
        for order, info in self.orders.items():
            for final_suborder in info.keys():
                self.obj += self.orders[order][final_suborder]['price'] * self.ksi[final_suborder]
        self.model.setObjective(self.obj, GRB.MAXIMIZE)

    def optimize_model(self):
        self.add_vars()
        self.model.update()
        self.add_subprod_constrs()
        self.add_order_constrs()
        self.add_equip_constrs()
        self.set_objective_function()
        self.model.write('model.lp')
        self.model.optimize()


if __name__ == '__main__':
    grbm = GRBModel()
    grbm.optimize_model()
    if grbm.model.Status == GRB.OPTIMAL:
        print(grbm.eps)
        print(grbm.b)
        print(grbm.c)

