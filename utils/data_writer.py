import plotly.express as px
import pandas as pd
import datetime as dt
from utils.gurobi_model import GRBModel
# from configs import output_file_name, days, move_hours, switch_hours
from configs import (output_file_name,
                     start_year, start_month, start_day,
                     days,
                     st_from, st_to,
                     mt_from, mt_to)


class Writer:

    def __init__(self):  # получение выходных данных
        self.grbm = GRBModel()
        self.eps, self.b, self.c, self.ksi = self.get_results()
        self.processed_suborders = self.get_processed_suborders()
        self.suborders_of_orders = self.get_suborders_of_orders()
        self.done_orders_info = self.transform_results()

    def get_results(self):  # получение результатов
        self.grbm.optimize_model()
        return self.grbm.eps, self.grbm.b, self.grbm.c, self.grbm.ksi

    def get_processed_suborders(self):  # список обработанных подзаказов
        return [suborder for (suborder, equip) in self.eps.keys() if self.eps[(suborder, equip)].X > 0]

    def get_suborders_of_orders(self):  # словарь заказ-->обработанные полуфабрикаты
        suborders_of_orders = {}
        for order, info in self.grbm.orders.items():
            suborders_of_orders[order] = []
            for final_suborder in info.keys():
                if self.ksi[final_suborder].X > 0 and final_suborder in self.processed_suborders:
                    suborders_of_orders[order].append(final_suborder)
        for order, suborders in suborders_of_orders.items():
            if suborders == list(self.grbm.orders[order].keys()):
                for subord in suborders:
                    for proc_subord in self.processed_suborders:
                        if proc_subord not in suborders and proc_subord not in self.grbm.final_subord_id and \
                                subord in self.grbm.order_graph[proc_subord]: suborders.append(proc_subord)
        return suborders_of_orders

    def transform_results(self):  # преобразование результатов
        list_of_dicts = []
        for (subord, equip) in self.eps.keys():
            for order, suborders in self.suborders_of_orders.items():
                if len(suborders) > 4 and self.eps[(subord, equip)].X > 0 and subord in suborders:
                    list_of_dicts.append({'Equipment_ID': str(equip), 'start': self.b[subord].X, 'end': self.c[subord].X,
                                          'Order_ID': str(order), 'Suborder_ID': str(subord)})
        return pd.DataFrame(list_of_dicts)

    def create_gantt_chart(self):  # построение диаграммы Ганта (+выходной файл excel)
        self.done_orders_info['Start'] = dt.datetime(start_year, start_month, start_day) + pd.TimedeltaIndex(self.done_orders_info['start'], unit='m')
        self.done_orders_info['End'] = dt.datetime(start_year, start_month, start_day) + pd.TimedeltaIndex(self.done_orders_info['end'], unit='m')
        self.done_orders_info = self.done_orders_info.drop(columns=['start', 'end'])
        self.done_orders_info.to_excel(output_file_name)
        discrete_map_resource = {'228': 'dodgerblue', '229': 'orangered', '230': 'hotpink', '231': 'mediumslateblue', '232': 'orange',
                                 '233': 'darkturquoise', '234': 'limegreen', '235': 'palegreen'}
        # discrete_map_resource = {'230': 'lightgray', '231': 'darkgray', '232': 'dimgray'}
        # fig = px.timeline(self.done_orders_info, x_start="Start", x_end="End", y="Equipment_ID", color="Order_ID", text="Suborder_ID",
        #                   color_discrete_map=discrete_map_resource, width=200, height=160)
        fig = px.timeline(self.done_orders_info, x_start="Start", x_end="End", y="Equipment_ID", color="Order_ID",
                          title=f'Schedule for {days} days, MT Disturbance: {mt_from}-{mt_to} min, ST Disturbance: {st_from}-{st_to} min',
                          width=1200, height=700, color_discrete_map=discrete_map_resource)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='whitesmoke')
        fig.update_layout(font_size=18, plot_bgcolor='white')
        fig.show()


if __name__ == '__main__':
    writer = Writer()
    writer.create_gantt_chart()
