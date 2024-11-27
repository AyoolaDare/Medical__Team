from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/clinic_management'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

username = 'ayoola'
password = 'Icu4cu46'

# Ensure proper bcrypt hashing
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

# Insert user
mongo.db.users.insert_one({
    'username': username, 
    'password': hashed_password,
    'role': 'doctor'
})

# Optional: Verify insertion
user = mongo.db.users.find_one({'username': username})
print("User inserted:", user)