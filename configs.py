input_file_name = '.\input-files\data.xlsx'  # входной файл
output_file_name = '.\output-files\schedule.xlsx'  # выходной файл

start_year = 2022  # начало периода планирования
start_month = 1
start_day = 1

days = 30  # дедлайн
deadline = days * 24 * 60
bigM = 100000  # константа для М-метода

# move_hours = 1.5
# move_disturb = move_hours * 60
#
# switch_hours = 0.5
# switch_disturb = switch_hours * 60

mt_from = 60  # границы для анализа чувствительности (перемещение)
mt_to = 90
st_from = 120  # границы для анализа чувствительности (переналадка)
st_to = 150
