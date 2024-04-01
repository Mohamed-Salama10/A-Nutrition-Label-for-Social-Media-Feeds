import pymongo 
from pymongo import MongoClient 
client = MongoClient("localhost", 27017)
try:
    # Use the admin database to send a ping command to the server.
    client.admin.command("ping")

    # If the ping is successful, print a message indicating a successful connection.
    print("pinged your deployment. You are connected to MongoDB")
except Exception as e:
    # If an exception occurs, print the exception message.
    print(e)
    

db = client.nutrition_project
user_collection = db["Users"]
Nutrition_collection = db["Nutrition"]