from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from functools import wraps
import pandas as pd
from datetime import datetime
import week_report
from apscheduler.schedulers.background import BackgroundScheduler
import io
app = Flask(__name__)
app.secret_key = 'supersecretkey'

scheduler = BackgroundScheduler()
scheduler.add_job(week_report.scheduled_weekly_job, 'cron', day_of_week='mon', hour=8, minute=5)
scheduler.start()

client = MongoClient('mongodb://mongo:lPjFpQVhrnCZlsErYLBeyxpgRltDXnzT@roundhouse.proxy.rlwy.net:47521')
db = client['Users']
users_collection = db['Users']
data_db = client['Data_Incoming']
data_collection = data_db['Data_Incoming']


# # Добавление тестового пользователя (однократно)
# def add_test_user():
#     existing_user = users_collection.find_one({"username": "testuser"})
#     if not existing_user:
#         users_collection.insert_one({
#             "username": "testuser",
#             "password": generate_password_hash("testpassword")
#         })

# add_test_user()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Неправильное имя пользователя или пароль"
    return render_template('login.html')


@app.route('/')
def home():
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect('/login')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/statistics')
@login_required
def statistics():
    documents = list(data_collection.find())
    return render_template('statistics.html', documents=documents)

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    client = MongoClient('mongodb://mongo:lPjFpQVhrnCZlsErYLBeyxpgRltDXnzT@roundhouse.proxy.rlwy.net:47521')
    db = client['Data_Incoming']
    collection = db['Data_Incoming']

    start_date = request.form['StartDate']
    end_date = request.form['EndDate']
    if start_date > end_date:
        return "Некорректные даты"
    file_format = request.form['FileFormat']
    include_lep = request.form['LEP']
    include_ps = request.form['PS']
    include_ru = request.form['VL']
    query = {
        "ДатаФормированияСообщения": {
            "$gte": start_date,
            "$lte": end_date
        }
    }
    exclude_events = []

    if include_lep == 'no':
     exclude_events.append("СозданиеЛЭП")
    if include_ps == 'no':
     exclude_events.append("СозданиеПодстанции")
    if include_ru == 'no':
     exclude_events.append("СозданиеРУ")
        
    if exclude_events:
            query["КодСобытия"] = {"$nin": exclude_events}


    print(query)
    # Преобразование строковых дат в объекты datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Получение всех документов из коллекции
    documents = list(collection.find(query))

    # Преобразование документов в DataFrame
    data = []
    for doc in documents:
        data.append({
            "РЭС": doc.get("РЭС", ""),
            "Тип": doc.get("КодСобытия", ""),
            "Код": doc.get("КодТехническогоОбъекта", ""),
            "ДатаФормированияСообщения": doc.get("ДатаФормированияСообщения", "")
        })

    df = pd.DataFrame(data)

    # Создание байтового потока для отчета
    output = io.BytesIO()

    if file_format == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', download_name='Отчёт.csv', as_attachment=True)
    else:
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='Отчёт.xlsx', as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)



