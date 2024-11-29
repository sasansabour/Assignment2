from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
#import urllib.parse
import pika
import json

app = Flask(__name__)

users = {}

password = "sS%4020242024"
#escaped_password = urllib.parse.quote_plus(password)
uri = f"mongodb+srv://sasansabour:{password}@cluster0.tuzcj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['user_database']  # The database
users_collection = db['users']  # Collection for user data

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue for the event
channel.queue_declare(queue='user_update_queue')


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    user_id = data['_id']
    #users[user_id] = data
    users_collection.insert_one(data)
    return jsonify({"message": "User created successfully"}), 201


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    # Update user data in the users collection
    result = users_collection.update_one({'_id': user_id}, {'$set': data})

    if result.modified_count > 0:
        # Publish the event to RabbitMQ
        event = {
            'user_id': user_id,
            'updated_data': data
        }
        channel.basic_publish(
            exchange='',
            routing_key='user_update_queue',
            body=json.dumps(event)
        )

        return jsonify({"message": "User updated and event published"}), 200
    else:
        return jsonify({"error": "User not found or no change detected"}), 404


if __name__ == '__main__':
    app.run(port=5001)
