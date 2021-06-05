# telegram_html5_game

The system use python3

## Install

1. Create bot, register game => token
2. Create proxy (I recommend to use ngrok) that forwards external https url (for telegram's webhooh) to http://localhost:5000 (flask server)
3. Start proxy, command for ngrok: `ngrok http 5000`
4. Create virtual env: `virtualenv --python=python3 venv`, `source venv/bin/activate`
5. Install requirement: `pip install -r requirements.txt`
6. Create `.env` file, check `.env.example`
7. Add list of stock codes (json format) to stock_codes.json
8. Start flask server: `python app.py`
