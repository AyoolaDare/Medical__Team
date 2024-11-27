from app import create_app, mongo
from datetime import datetime
from bson import ObjectId

app = create_app()

def update_timestamps():
    with app.app_context():
        patients = mongo.db.patients.find({})
        for patient in patients:
            if 'medical_records' in patient:
                updated = False
                for record in patient['medical_records']:
                    if 'timestamp' not in record:
                        if 'date' in record:
                            record['timestamp'] = record['date']
                        else:
                            record['timestamp'] = datetime.utcnow()
                        updated = True
                if updated:
                    mongo.db.patients.update_one(
                        {'_id': ObjectId(patient['_id'])},
                        {'$set': {'medical_records': patient['medical_records']}}
                    )
        print("All existing medical records have been updated with timestamps.")

if __name__ == "__main__":
    update_timestamps()

