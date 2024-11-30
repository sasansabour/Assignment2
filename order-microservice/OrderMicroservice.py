from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
#import urllib.parse
import pika
import json
import threading

app = Flask(__name__)

orders = {}

password = "sS%4020242024"
#escaped_password = urllib.parse.quote_plus(password)
uri = f"mongodb+srv://sasansabour:{password}@cluster0.tuzcj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['order_database']  # The database
orders_collection = db['orders']  # Collection for orders data

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq',heartbeat=60, retry_delay=5, socket_timeout=60))
channel = connection.channel()

# Declare the queue where user update events will be published
channel.queue_declare(queue='user_update_queue')


def callback(ch, method, properties, body):
    event = json.loads(body)
    user_id = event['user_id']
    updated_data = event['updated_data']

    # Update the orders with the new user email or delivery address
    orders_collection.update_many(
        {'user_id': user_id},  # Filter orders by user_id
        {'$set': updated_data}  # Update orders with new user info
    )


    print(f"Updated orders for user {user_id} with new data {updated_data}")


def start_event_listener():
    # Consume the messages from the queue
    channel.basic_consume(queue='user_update_queue', on_message_callback=callback, auto_ack=True)

    print("Waiting for user update events. To exit press CTRL+C")
    channel.start_consuming()


@app.route('/order', methods=['POST'])
def create_order():
    print('hi')
    data = request.json
    print(data)
    order_id = data['order_id']
    #orders[order_id] = data
    orders_collection.insert_one(data)
    return jsonify({"message": "Order created successfully"}), 201


@app.route('/order/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    # Update order status in the orders collection
    result = orders_collection.update_one({'order_id': order_id}, {'$set': data})

    if result.modified_count > 0:
        return jsonify({"message": "Order updated successfully"}), 200
    else:
        return jsonify({"error": "Order not found or no change detected"}), 404


@app.route('/order', methods=['GET'])
def get_orders():
    print(request.args)
    status = request.args.get('status')
    print(status)
    orderStatus = orders_collection.find({'status': status})
    orders_list = []
    for order in orderStatus:
        order['_id'] = str(order['_id'])  # Convert ObjectId to string
        orders_list.append(order)

    return jsonify(orders_list), 200


if __name__ == '__main__':

    threading.Thread(target=start_event_listener, daemon=True).start()

    app.run(host='0.0.0.0', port=5002)
