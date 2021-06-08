import os
import urllib

import telegram
import pymongo as mg
from dotenv import load_dotenv
import flask
from flask import Flask, request, render_template, json

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
        send_from = update["callback_query"].to_dict()["from"]
        user = {
            "user_id": send_from["id"],
            "user_name": send_from["username"],
            "user_firstname": send_from["first_name"],
            "user_lastname": send_from["last_name"],
        }
        try:
            bot.answer_callback_query(
                callback_query_id,
                url=url + 'game?' + urllib.parse.urlencode(user)
            )
        except Exception as e:
            bot.answer_callback_query(callback_query_id, str(e))
    return "ok"


@app.route("/game", methods=["GET"])
def game():
    user_id = request.args.get("user_id")
    user_name = request.args.get("user_name")
    user_first_name = request.args.get("user_firstname")
    user_last_name = request.args.get("user_lastname")
    user = my_collection.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "user_name": user_name,
            "user_firstname": user_first_name,
            "user_lastname": user_last_name,
        }
    else:
        del user["_id"]
    return render_template(
        "index.html",
        data={
            "url": url,
            "stock_codes": ut.load_data(STOCK_CODES_FILE),
            "user": user,
        }
    )


def add_headers(response):
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')


@app.route("/submit", methods=["POST", "OPTIONS"])
def submit():
    if request.method == "OPTIONS":
        response = flask.jsonify({})
        add_headers(response)
        return response
    print(request.data)
    data = json.loads(request.data)
    print(data)
    saved = False
    user = my_collection.find_one({"user_id": data["user_id"]})
    if user:
        existing_answer_names = [answer["name"] for answer in user["answers"]]
        if data["answer"]["name"] not in existing_answer_names:
            user["answers"].append(data["answer"])
            my_collection.update_one(
                {"user_id": data.get("user_id")},
                {"$set": {"answers": user["answers"]}}
            )
            saved = True
    else:
        my_collection.insert_one({
            "user_id": data["user_id"],
            "user_name": data["user_name"],
            "user_firstname": data["user_firstname"],
            "user_lastname": data["user_lastname"],
            "answers": [data["answer"]]
        })
        saved = True
    if saved:
        res = {
            "result": True,
            "message":  "Success",
        }
    else:
        res = {
            "result": False,
            "message": "Answer name already exists",
        }
    res = flask.jsonify(res)
    add_headers(res)
    return res

def set_webhook():
    s = bot.setWebhook(url)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    print(set_webhook())
    app.run(threaded=True)
