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


def sort_sheet_by_column(sheet, start_row=3, sort_col=7):
    data = sheet.get_all_values()

    # Trenne Kopfbereich und Sortierbereich
    header = data[:start_row - 1]
    data_to_sort = data[start_row - 1:]

    # Leere Zeilen filtern (optional)
    data_to_sort = [row for row in data_to_sort if any(cell.strip() for cell in row)]

    # Sortieren nach der gewünschten Spalte
    data_sorted = sorted(
        data_to_sort,
        key=lambda row: row[sort_col - 1] if len(row) >= sort_col and row[sort_col - 1] else '999999'
    )

    # Neue kombinierte Daten
    new_data = header + data_sorted

    # Sheet-Zeilen aktualisieren (bestehende Zeilen werden ersetzt)
    for i, row in enumerate(new_data):
        sheet.insert_row(row, index=i + 1)
        sheet.delete_rows(i + 2)



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

    sort_sheet_by_column(sheet, start_row=3)

    return jsonify({
        "response_type": "in_channel",
        "text": f"📝 Eingetragen: *{text}* in Zeile {insert_after + 1}"
    })
