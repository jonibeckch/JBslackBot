import requests
import os
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

@app.route("/tobuy", methods=["POST"])
def handle_tobuy():
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
        
@app.route("/todo", methods=["POST"])
def handle_todo():
    text = request.form.get("text")

    # Neuen Eintrag hinzufügen
    sheet.append_row([datetime.now().isoformat(), text])

    return jsonify({
        "response_type": "in_channel",
        "text": f"📝 Eintrag hinzugefügt: *{text}*"
    })
