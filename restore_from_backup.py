from pymongo import MongoClient

def restore_users(backup_date):
    # Подключение к серверу MongoDB
    client = MongoClient('mongodb://localhost:27017')
    
    # Название основной базы данных и коллекции
    target_db_name = 'Users'
    target_db = client[target_db_name]
    
    # Название базы данных бэкапа
    backup_db_name = f'Users_{backup_date}'
    backup_db = client[backup_db_name]
    
    # Проверка существования базы данных бэкапа
    if backup_db_name not in client.list_database_names():
        print(f"Backup database {backup_db_name} does not exist.")
        return
    
    # Очистка коллекций в основной базе данных
    for collection_name in target_db.list_collection_names():
        target_db[collection_name].delete_many({})
    
    # Копирование коллекций из базы данных бэкапа в основную базу данных
    for collection_name in backup_db.list_collection_names():
        backup_collection = backup_db[collection_name]
        target_collection = target_db[collection_name]
        target_collection.insert_many(backup_collection.find())
    
    print(f"Restored {target_db_name} from {backup_db_name}")

if __name__ == '__main__':
    # Укажите дату бэкапа в формате YYYYMMDD
    backup_date = '20240601'
    restore_users(backup_date)
