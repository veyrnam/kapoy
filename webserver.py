from flask import Flask
from threading import Thread

app = Flask(__name__)  # Use __name__ instead of ''

@app.route('/')
def home():
    return "discord bot is running!"

def run():
    # Disable debug mode for production
    app.run(host="0.0.0.0", port=8080, debug=False)

def keep_alive():
    # Daemon thread ensures it won't block program exit
    t = Thread(target=run, daemon=True)
    t.start()
