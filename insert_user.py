from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# Подключение к MongoDB
try:
    client = MongoClient('mongodb://mongo:lPjFpQVhrnCZlsErYLBeyxpgRltDXnzT@roundhouse.proxy.rlwy.net:47521')
    db = client['Users']
    users_collection = db['Users']

    # Добавление тестового пользователя
    user = {
        "username": "admin",
        "password": generate_password_hash("admin")
    }

    result = users_collection.insert_one(user)
    print(f"User inserted with id: {result.inserted_id}")

except Exception as e:
    print(f"An error occurred: {e}")
