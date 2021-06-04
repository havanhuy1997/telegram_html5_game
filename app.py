from flask import Flask, request, render_template
import telegram

TOKEN = "1896126168:AAE-5B0QoUTDwseJjifWgpWEidjhLc50u38"
URL = "https://1c28b57f51d1.ngrok.io/"

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
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    print(request.data)


def set_webhook():
   s = bot.setWebhook(URL)
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"


if __name__ == '__main__':
    print(set_webhook())
    app.run(threaded=True)