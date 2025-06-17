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

TODO_CHANNEL_ID = "C0903PT3SJK"  # Channel-ID von #todo
TODO_CHANNEL_ID = "C090LFMCE9Y"  # Channel-ID von #tobuy

@app.route("/wakeup", methods=["POST"])
def handle_wakeup():
        return jsonify({
            "response_type": "in_channel",
            "text": f"Ich bin schon wach!"
        })

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

    # Zeile, nach der eingefügt werden soll
    insert_after = 25

    # Eine neue Zeile nach Zeile 25 einfügen
    sheet.insert_row([], index=insert_after + 1)

    # Werte setzen
    sheet.update_cell(insert_after + 1, 2, "98")          # Spalte B
    sheet.update_cell(insert_after + 1, 4, text)          # Spalte D (Slack-Text)
    sheet.update_cell(insert_after + 1, 7, f'=IF(ISBLANK(F{insert_after + 1});B{insert_after + 1};(-F{insert_after + 1})+46500)')  # Spalte G

    return jsonify({
        "response_type": "in_channel",
        "text": f"📝 Eingetragen: *{text}* in Zeile {insert_after + 1}"
    })


@app.route("/events", methods=["POST"])
def slack_events():
    data = request.get_json()

    # Verifizierung bei Event-Registrierung
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

    if data.get("type") == "event_callback":
        event = data.get("event", {})
        channel = event.get("channel")
        text = event.get("text")

        if event.get("type") == "message" and "subtype" not in event:
            if channel == TODO_CHANNEL_ID:
                return handle_todo(text)
            elif channel == TOBUY_CHANNEL_ID:
                return handle_tobuy(text)

    return "", 200

# === Handler: /todo ===
def handle_todo(text):
    insert_after = 25
    sheet.insert_row([], index=insert_after + 1)
    sheet.update_cell(insert_after + 1, 2, "98")  # Spalte B
    sheet.update_cell(insert_after + 1, 4, text)  # Spalte D
    sheet.update_cell(insert_after + 1, 7, f'=IF(ISBLANK(F{insert_after + 1});B{insert_after + 1};(-F{insert_after + 1})+46500)')  # Spalte G
    return "", 200

# === Handler: /tobuy ===
def handle_tobuy(text):
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
        print(f"Trello-Karte erstellt: {text}")
    else:
        print(f"Fehler beim Erstellen: {response.text}")
    return "", 200

