import boto3
from botocore.exceptions import ClientError
from config import Config
from flask_bcrypt import Bcrypt
import uuid

def add_user(username, password, role):
    dynamodb = boto3.resource('dynamodb',
                              region_name=Config.AWS_REGION,
                              aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)

    table = dynamodb.Table('clinic_users')
    bcrypt = Bcrypt()

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'username': username,
                'password': hashed_password,
                'role': role
            }
        )
        print(f"User {username} added successfully with role: {role}")
    except ClientError as e:
        print(f"Error adding user: {e}")

if __name__ == "__main__":
    while True:
        username = input("Enter username (or 'q' to quit): ")
        if username.lower() == 'q':
            break
        password = input("Enter password: ")
        role = input("Enter role: ")
        add_user(username, password, role)

    print("User creation complete.")