from utils.data_writer import Writer
from datetime import datetime

start_time = datetime.now()  # отслеживание времени выполнения программы
writer = Writer()
writer.create_gantt_chart()  # запуск
end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
