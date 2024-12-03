import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
import bcrypt
from config import Config

dynamodb = boto3.resource('dynamodb',
                          region_name=Config.AWS_REGION,
                          aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)

users_table = dynamodb.Table(Config.USERS_TABLE_NAME)
patients_table = dynamodb.Table(Config.PATIENTS_TABLE_NAME)
activities_table = dynamodb.Table(Config.ACTIVITIES_TABLE_NAME)

class User:
    @staticmethod
    def create(username, password, role):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        try:
            users_table.put_item(
                Item={
                    'id': user_id,
                    'username': username,
                    'password': hashed_password,
                    'role': role
                }
            )
            return True
        except ClientError as e:
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def get_by_username(username):
        try:
            response = users_table.scan(
                FilterExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            print(f"Error getting user: {e}")
            return None

    @staticmethod
    def check_password(user, password):
        return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))

class Patient:
    @staticmethod
    def create(first_name, last_name, phone_number, age=None):
        patient_id = str(uuid.uuid4())
        try:
            item = {
                'id': patient_id,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'created_at': datetime.utcnow().isoformat()
            }
            if age is not None:
                item['age'] = int(age)
            
            patients_table.put_item(Item=item)
            return patient_id
        except ClientError as e:
            print(f"Error creating patient: {e}")
            return None

    @staticmethod
    def get_all():
        try:
            response = patients_table.scan()
            return response['Items']
        except ClientError as e:
            print(f"Error getting all patients: {e}")
            return []

    @staticmethod
    def get_by_id(patient_id):
        try:
            response = patients_table.get_item(Key={'id': patient_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting patient: {e}")
            return None

    @staticmethod
    def update(patient_id, data):
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            for key, value in data.items():
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
            update_expression = update_expression.rstrip(", ")

            patients_table.update_item(
                Key={'id': patient_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return True
        except ClientError as e:
            print(f"Error updating patient: {e}")
            return False

    @staticmethod
    def add_medical_record(patient_id, record):
        try:
            if 'timestamp' not in record:
                record['timestamp'] = datetime.utcnow().isoformat()
            
            patients_table.update_item(
                Key={'id': patient_id},
                UpdateExpression="SET medical_records = list_append(if_not_exists(medical_records, :empty_list), :record)",
                ExpressionAttributeValues={
                    ':record': [record],
                    ':empty_list': []
                }
            )
            return True
        except ClientError as e:
            print(f"Error adding medical record: {e}")
            return False

    @staticmethod
    def search(query):
        try:
            response = patients_table.scan(
                FilterExpression='contains(first_name, :q) OR contains(last_name, :q) OR contains(phone_number, :q)',
                ExpressionAttributeValues={':q': query}
            )
            return response['Items']
        except ClientError as e:
            print(f"Error searching patients: {e}")
            return []

class Activity:
    @staticmethod
    def create(patient_id, patient_name, action, admin_name, admin_role):
        activity_id = str(uuid.uuid4())
        try:
            activities_table.put_item(
                Item={
                    'id': activity_id,
                    'patient_id': patient_id,
                    'patient_name': patient_name,
                    'action': action,
                    'admin_name': admin_name,
                    'admin_role': admin_role,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            return activity_id
        except ClientError as e:
            print(f"Error creating activity: {e}")
            return None

    @staticmethod
    def get_recent(limit=10):
        try:
            response = activities_table.scan(Limit=limit)
            return sorted(response['Items'], key=lambda x: x['timestamp'], reverse=True)
        except ClientError as e:
            print(f"Error getting recent activities: {e}")
            return []

    @staticmethod
    def get_all():
        try:
            response = activities_table.scan()
            return sorted(response['Items'], key=lambda x: x['timestamp'], reverse=True)
        except ClientError as e:
            print(f"Error getting all activities: {e}")
            return []

