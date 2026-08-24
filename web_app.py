import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session

from brain.classifier import classify
from web_actions import execute_web
from memory.storage_manager import StorageManager
from config import MODEL_PATH

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()


def ensure_model_trained():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Training now...")
        from brain.trainer import train
        train()
        print("Training complete.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"response": "Please say something!", "action": "message"})

    flow_state = session.get("flow_state")

    if flow_state == "awaiting_name":
        session["save_name"] = message
        session["flow_state"] = "awaiting_content"
        session.modified = True
        return jsonify({
            "response": "Got it. Now, what content do you want to save?",
            "action": "message"
        })

    if flow_state == "awaiting_content":
        name = session.pop("save_name", "note")
        content = message
        session.pop("flow_state", None)
        session.modified = True

        sm = StorageManager()
        path = sm.save_text(name, content, tags=name)
        return jsonify({
            "response": f"Saved! Your file '{name}' is stored at: {path}",
            "action": "message"
        })

    intent, confidence, entity = classify(message)
    result = execute_web(intent, entity, message)

    if result.get("action") == "save_flow":
        session["flow_state"] = "awaiting_name"
        session.modified = True
        return jsonify({
            "response": "What would you like to name this file?",
            "action": "message"
        })

    return jsonify(result)


if __name__ == "__main__":
    ensure_model_trained()
    print("Nexus Web App running at http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
