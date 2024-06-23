from flask import Flask
from pymongo import MongoClient
import pandas as pd
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)


# Функция для извлечения данных за последнюю неделю
def fetch_weekly_data():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Data_Incoming']
    collection = db['Data_Incoming']
    
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    
    query = {
        "ДатаФормированияСообщения": {
            "$gte": start_date.strftime("%Y-%m-%d"),
            "$lt": end_date.strftime("%Y-%m-%d")
        }
    }
    # print(query)
    data = list(collection.find(query))
    print(data)
    return data
def generate_report(data):
    df = pd.DataFrame(data)
    report_name = f'Эженедельный_ОТЧЕТ_{datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx'
    df.to_excel(report_name, index=False)
    return report_name
def send_email(report_name):
    sender_email = 'leobusov@yandex.ru'
    receiver_email = 'russiadreamer@gmail.com'
    subject = 'Еженедельный отчет'
    body = 'Во вложении находится еженедельный отчет.'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(report_name, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), Name=report_name)
        part['Content-Disposition'] = f'attachment; filename="{report_name}"'
        msg.attach(part)

    with smtplib.SMTP('smtp.yandex.ru', 587) as server:
        server.starttls()
        server.login(sender_email, 'vmlathyxqmhqwdvw')
        server.sendmail(sender_email, receiver_email, msg.as_string())

def scheduled_weekly_job():
    data = fetch_weekly_data()
    if data:
        report_name = generate_report(data)
        send_email(report_name)

# scheduled_weekly_job()

# scheduler = BackgroundScheduler()
# scheduler.add_job(scheduled_weekly_job, 'cron', day_of_week='mon', hour=9, minute=15)
# scheduler.start()
@app.route('/')
def home():
    return "Welcome to the automated reporting system!"

if __name__ == '__main__':
    app.run(debug=True)

