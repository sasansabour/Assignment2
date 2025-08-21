import os
import random
from flask import Flask, request, jsonify
import requests
import json


app = Flask(__name__)

# Configuration
USER_SERVICE_V1 = os.getenv('USER_SERVICE_V1')
USER_SERVICE_V2 = os.getenv('USER_SERVICE_V2')
ORDER_SERVICE = os.getenv('ORDER_SERVICE')

# Configuration: Read P (percentage of traffic to v1) from a configuration file or environment variable
with open('config.json') as config_file:
    config = json.load(config_file)
    P = config.get('P', 80)  # Default to 80% to v1 if not specified


# Define routes to forward requests
@app.route('/user', methods=['POST', 'PUT'])
@app.route('/user/<user_id>', methods=['PUT'])
def user_service(user_id=None):
    """Forward requests to the User Microservice"""
    # Randomly route P% of traffic to v1 and (100 - P)% to v2
    route_to_v1 = random.randint(1, 100) <= P

    if route_to_v1:
        user_service_url = f"{USER_SERVICE_V1}/user/{user_id}" if user_id else f"{USER_SERVICE_V1}/user"
    else:
        user_service_url = f"{USER_SERVICE_V2}/user/{user_id}" if user_id else f"{USER_SERVICE_V2}/user"

    response = requests.request(
        method=request.method,
        url=user_service_url,
        json=request.json
    )
    return jsonify(response.json()), response.status_code


@app.route('/order', methods=['GET', 'POST'])
@app.route('/order/<order_id>', methods=['PUT'])
def order_service(order_id=None):
    """Forward requests to the Order Microservice"""
    
    if request.method == 'GET':
        data = request.args.to_dict()
        response = requests.get(f"{ORDER_SERVICE}/order", params=data)
    else:
        data = request.json
        order_service_url = f"{ORDER_SERVICE}/order/{order_id}" if order_id else f"{ORDER_SERVICE}/order"
        response = requests.request(method=request.method,url=order_service_url,json=data)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
