from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

password = "sS@20242024"
escaped_password = urllib.parse.quote_plus(password)
uri = f"mongodb+srv://sasansabour:{escaped_password}@cluster0.tuzcj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
# Access the user and order databases
user_db = client["user_database"]
order_db = client["order_database"]

user_collection = user_db["users"]
order_collection = order_db["orders"]

def print_hi():

    try:


        # Insert a user document
        """
        user_document = {
            "_id": "user123",
            "email": "user@example.com",
            "delivery_address": "123 Main St, Cityville"
        }
        user_collection.insert_one(user_document)

        # Insert an order document
        order_document = {
            "order_id": "order456",
            "user_id": "user123",
            "items": ["item1", "item2"],
            "email": "user@example.com",
            "delivery_address": "123 Main St, Cityville",
            "status": "under process"
        }
        order_collection.insert_one(order_document)
        """
        updated_user = user_collection.find_one({"_id": "user123"})
        print("Updated User Document:", updated_user)

        # Check the updated order documents
        updated_orders = order_collection.find({"user_id": "user123"})
        for order in updated_orders:
            print("Updated Order Document:", order)

    except Exception as e:
        print(e)

def synchronize_user_data(user_id, new_email=None, new_address=None):
    # Update the user database
    update_fields = {}
    if new_email:
        update_fields["email"] = new_email
    if new_address:
        update_fields["delivery_address"] = new_address

    if update_fields:
        user_collection.update_one({"_id": user_id}, {"$set": update_fields})

        # Update the order database for all orders of the user
        order_collection.update_many(
            {"user_id": user_id},
            {"$set": update_fields}
        )
        print(f"Data synchronized for user: {user_id}")

# Example of updating email and delivery address

if __name__ == '__main__':
    print_hi()
    #synchronize_user_data("user123", new_email="new_email@example.com", new_address="456 Elm St, Cityville")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
