import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, mongo
from datetime import datetime

app = create_app()

def add_created_at_field():
    with app.app_context():
        patients = mongo.db.patients.find({'created_at': {'$exists': False}})
        for patient in patients:
            mongo.db.patients.update_one(
                {'_id': patient['_id']},
                {'$set': {'created_at': patient['_id'].generation_time}}
            )
        print("Migration completed: 'created_at' field added to existing patient records.")

if __name__ == "__main__":
    add_created_at_field()

