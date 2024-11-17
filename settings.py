import json
import telegram
import sqlite3

token = None
dbname = "db.db"

with open("main_data.json") as data_json:
    token = json.load(data_json)["token"]

db = sqlite3.connect(database=dbname, check_same_thread=False)
cursor = db.cursor()

bot = telegram.Bot(token=token)

