from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database'
mongo = PyMongo(app)

# Test connection
try:
    mongo.db.command('ping')
    print("Successfully connected to MongoDB")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

# Test user retrieval
user = mongo.db.users.find_one({'username': 'ayooladare'})
print("Retrieved user:", user)