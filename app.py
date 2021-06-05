import pymongo as mg
from flask import Flask, request, render_template
import json
import telegram
TOKEN = "1896126168:AAE-5B0QoUTDwseJjifWgpWEidjhLc50u38"
URL = "https://49ea31162ed9.ngrok.io/"


clientMongo = mg.MongoClient("mongodb://localhost:27017/")
mydb = clientMongo["DBPortfolio"]
myCollection = mydb["collectionPortfolio"]
listDB = clientMongo.list_database_names()
if listDB:
    print("Connected to MongoDB")
    print(f"Database : {listDB}")


bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)


@app.route("/", methods=["POST"])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update["callback_query"]:
        callback_query_id = update["callback_query"]["id"]
        print(callback_query_id)
        try:
            bot.answer_callback_query(callback_query_id, url=URL + 'game')
        except Exception as e:
            bot.answer_callback_query(callback_query_id, str(e))
    return "ok"


@app.route("/game", methods=["GET"])
def game():
    return render_template("index.html",URL=URL)


result = {}


@app.route("/submit", methods=["POST"])
def submit():
    print(request.data)
    result = (request.data)
    record = json.loads(result)
    name  = record["name"]
    if checkName(name):
        print("Name already exists")
        return {"status":"Name already exists"}
    else: 
        writeToDB(result)
        print("name satisfied")
        return {"status":"Name satisfied"}
       
    # return request.data


def writeToDB(result):
    print('Write to DB')
    record = json.loads(result)
    myCollection.insert_one(record)


def checkName(name):
    print("check name")
    resultQuery = myCollection.find({}, {"_id": 0, "name": 1})
    lsName = []
    for i in resultQuery:
        # print(i["name"])
        lsName.append(i["name"])
    if name in lsName:
        return True
    else:
        return False


def set_webhook():
    s = bot.setWebhook(URL)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    print(set_webhook())
    app.run(threaded=True)
