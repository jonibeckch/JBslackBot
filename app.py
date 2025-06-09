from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/slack/todo", methods=["POST"])
def todo():
    user = request.form.get("user_name")
    text = request.form.get("text")
    return jsonify({
        "response_type": "in_channel",
        "text": f":white_check_mark: {user} hat ein neues To-Do erstellt: *{text}*"
    })

if __name__ == "__main__":
    app.run()
