from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/slash", methods=["POST"])
def handle_slash():
    text = request.form.get("text")
    return jsonify({
        "response_type": "in_channel",
        "text": f"Todo empfangen: *{text}*"
    })

if __name__ == "__main__":
    app.run()
