import psycopg2


# пытаемся подключиться к базе данных
conn = psycopg2.connect(dbname='AviaGram', user='postgres', password='postgres', host='localhost')
cursor_obj = conn.cursor()



print('ok')

