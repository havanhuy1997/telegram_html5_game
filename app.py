import os

import telegram
import pymongo as mg
from dotenv import load_dotenv
from flask import Flask, request, render_template

import utils as ut

load_dotenv()

STOCK_CODES_FILE = "stock_codes.json"

token = os.getenv("TOKEN")
url = os.getenv("HOST")

client_mongo = mg.MongoClient(f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/")
mydb = client_mongo[os.getenv("MONGO_DB")]
my_collection = mydb[os.getenv("MONGO_COLLECTION")]

bot = telegram.Bot(token=token)
app = Flask(__name__)


@app.route("/", methods=["POST"])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update["callback_query"]:
        callback_query_id = update["callback_query"]["id"]
        print(callback_query_id)
        try:
            bot.answer_callback_query(callback_query_id, url=url + 'game')
        except Exception as e:
            bot.answer_callback_query(callback_query_id, str(e))
    return "ok"


@app.route("/game", methods=["GET"])
def game():
    return render_template(
        "index.html",
        data={"url": url, "stock_codes": ut.load_data(STOCK_CODES_FILE)}
    )


@app.route("/submit", methods=["POST"])
def submit():
    data = request.data
    print(data)
    if my_collection.find({"name": data.get("name")}).count() > 0:
        return {
            "result": False,
            "message": "Name already exists",
        }
    else:
        my_collection.insert_one(data)
        return {
            "result": True,
            "message":  "Success",
        }

def set_webhook():
    s = bot.setWebhook(url)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    print(set_webhook())
    app.run(threaded=True)
