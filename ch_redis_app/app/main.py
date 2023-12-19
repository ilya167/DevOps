import json
import threading
import redis
from clickhouse_driver import Client
import requests
import logging


redis_client = redis.Redis(host='localhost', port='6379', db=0, password='')
ch_client = Client(host='localhost', port='9000', user='default', password= '')

def process_queue():
    while True:
        task = redis_client.blpop('search_queue')
        task_id, task_data = task
        task_data = json.loads(task_data)
        ipv4 = task_data['ipv4']
        mac = task_data['mac']
        search(ipv4, mac)
        
def pastebin_upload(user):
    data = {
        'api_option': 'paste',
        'api_dev_key': "gkzrVghBRZeVlwKB4yJCq-u1Bl_fAZzX",
        'api_paste_code': json.dumps(user),
        'api_paste_format': 'json'
        }
    r = requests.post("https://pastebin.com/api/api_post.php", data=data)
    url = r.url
    with open('urls.txt', 'a') as file:
        file.write(user['username'] + ': ' + (r.content.decode('UTF-8')) + '\n')
        logging.info(f'Successful search: {url}')
        print(user['username'] + ': ' + (r.content.decode('UTF-8')) + '\n')
    return r.content.decode('UTF-8')
    


def search_user(ipv4, mac):
    query = f"SELECT username, ipv4, mac FROM test_table WHERE ipv4 = '{ipv4}' AND mac = '{mac}'"
    try:
        result = ch_client.execute(query)
        if result:
            return {
                "username": result[0][0],
                "ipv4": result[0][1],
                "mac": result[0][2]
            }
    except Exception as e:
        print("Error while searching username: {e}")
    return None

def search(ipv4, mac):
    user = search_user(ipv4, mac)
    url = pastebin_upload(user)

print("Waiting for queue from redis")
if __name__ == '__main__':
    num_threads = 4
    for _ in range(num_threads):
        thread = threading.Thread(target=process_queue)
        thread.start()