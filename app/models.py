from app import mongo, bcrypt
from bson.objectid import ObjectId
from datetime import datetime

class User:
    @staticmethod
    def create(username, password, role):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password,
            'role': role
        })

    @staticmethod
    def get_by_username(username):
        return mongo.db.users.find_one({'username': username})

    @staticmethod
    def check_password(user, password):
        return bcrypt.check_password_hash(user['password'], password)

class Patient:
    @staticmethod
    def create(first_name, last_name, phone_number):
        try:
            result = mongo.db.patients.insert_one({
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'medical_records': [],
                'created_at': datetime.utcnow()
            })
            return result.inserted_id
        except Exception as e:
            print(f"Error creating patient: {e}")
            return None

    @staticmethod
    def get_all():
        return list(mongo.db.patients.find())

    @staticmethod
    def get_by_id(patient_id):
        return mongo.db.patients.find_one({'_id': ObjectId(patient_id)})

    @staticmethod
    def update(patient_id, data):
        try:
            mongo.db.patients.update_one(
                {'_id': ObjectId(patient_id)}, 
                {'$set': data}
            )
            return True
        except Exception as e:
            print(f"Error updating patient: {e}")
            return False

    @staticmethod
    def add_medical_record(patient_id, record):
        try:
            if 'timestamp' not in record:
                record['timestamp'] = datetime.utcnow()
            
            mongo.db.patients.update_one(
                {'_id': ObjectId(patient_id)},
                {'$push': {'medical_records': record}}
            )
            return True
        except Exception as e:
            print(f"Error adding medical record: {e}")
            return False

    @staticmethod
    def search(query):
        return list(mongo.db.patients.find({
            '$or': [
                {'first_name': {'$regex': query, '$options': 'i'}},
                {'last_name': {'$regex': query, '$options': 'i'}},
                {'phone_number': {'$regex': query, '$options': 'i'}}
            ]
        }))

class Activity:
    @staticmethod
    def create(patient_id, patient_name, action, admin_name, admin_role):
        try:
            activity = {
                'patient_id': str(patient_id),
                'patient_name': patient_name,
                'action': action,
                'admin_name': admin_name,
                'admin_role': admin_role,
                'timestamp': datetime.utcnow()
            }
            result = mongo.db.activities.insert_one(activity)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating activity: {e}")
            return None

    @staticmethod
    def get_recent(limit=10):
        try:
            return list(mongo.db.activities.find().sort('timestamp', -1).limit(limit))
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []

    @staticmethod
    def get_all():
        try:
            return list(mongo.db.activities.find().sort('timestamp', -1))
        except Exception as e:
            print(f"Error getting all activities: {e}")
            return []
