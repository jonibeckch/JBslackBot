import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

@app.route("/slash", methods=["POST"])
def handle_slash():
    text = request.form.get("text")

    # Trello-Karte erstellen
    response = requests.post(
        "https://api.trello.com/1/cards",
        params={
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN,
            "idList": TRELLO_LIST_ID,
            "name": text
        }
    )

    if response.status_code == 200:
        return jsonify({
            "response_type": "in_channel",
            "text": f"📋 Karte erstellt: *{text}*"
        })
    else:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Fehler beim Erstellen: {response.text}"
        })
