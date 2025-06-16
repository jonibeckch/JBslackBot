import requests
import os
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

app = Flask(__name__)

#Umgebungsvariablen für Trello Laden
TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

#Umgebungsvariablen für Google Laden
creds_json = os.getenv("GOOGLE_CREDS_JSON")
creds_dict = json.loads(creds_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SHEET_ID).sheet1



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

    sheet.append_row(["Test2", text])

    return jsonify({
        "response_type": "in_channel",
        "text": f"📝 Eintrag hinzugefügt: *{text}*"
    })
