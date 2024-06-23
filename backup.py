from pymongo import MongoClient
import datetime

def backup_users():
    # Подключение к серверу MongoDB
    client = MongoClient('mongodb://localhost:27017')
    
    # Название основной базы данных и коллекции
    source_db_name = 'Users'
    source_db = client[source_db_name]
    
    # Создание имени для базы данных бэкапа
    today = datetime.datetime.today().strftime('%Y%m%d')
    backup_db_name = f'Users_{today}'
    backup_db = client[backup_db_name]
    
    # Копирование коллекций из основной базы данных в базу данных бэкапа
    for collection_name in source_db.list_collection_names():
        source_collection = source_db[collection_name]
        backup_collection = backup_db[collection_name]
        backup_collection.insert_many(source_collection.find())
    
    print(f"Backup for {source_db_name} created as {backup_db_name}")

if __name__ == '__main__':
    backup_users()
