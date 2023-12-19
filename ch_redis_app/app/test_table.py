from faker import Faker
from clickhouse_driver import Client
import ipaddress
import random

fake = Faker()

# Подключение к ClickHouse
client = Client(host='localhost', port='9000', user='default', password= '')

# Создание таблицы с полями username, ipv4, mac
client.execute('CREATE TABLE IF NOT EXISTS test_table (username String, ipv4 String, mac String) ENGINE = MergeTree() ORDER BY username')

# Генерация и запись тестовых данных в таблицу
for _ in range(10):  # Генерация 10 записей
    username = fake.user_name()
    ipv4 = ipaddress.IPv4Address(random.getrandbits(32)).exploded
    mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
    client.execute('INSERT INTO test_table (username, ipv4, mac) VALUES', [(username, ipv4, mac)])
