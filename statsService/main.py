import json
from flask import Flask, Response
import clickhouse_connect
from kafka import KafkaConsumer

app = Flask(__name__)


def createConsumer():
    while True:
        try:
            prod = KafkaConsumer('events', bootstrap_servers='kafka:29092')
            return prod
        except:
            continue

consumer = createConsumer()

def consume_messages():
    for message in consumer:
        value = message.value.decode('ascii')
        value = json.loads(value)
        print(value, flush=True)
        if 'user_id' not in value:
            value['user_id'] = None 
        client.insert('stats.main', [[value['task_id'], value['user_id'], value['type']]], column_names=['task_id', 'user_id', 'type'])

client = clickhouse_connect.get_client(host='clickhouse')

@app.route('/stats', methods=['GET'])
def get_stats():
    return Response(status=200)

if __name__ == '__main__':
    from threading import Thread
    t = Thread(target=consume_messages)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=5010)
