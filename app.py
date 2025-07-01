from flask import Flask, render_template_string
import os
import time

app = Flask(__name__)

LOG_FILE = "dialogue_log.txt"
MANUAL_INSERT_FILE = "third_voice_insert.txt"

def append_to_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def get_last_speaker():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.startswith("[") and "]" in line:
                    parts = line.split("] ")
                    if len(parts) > 1 and ": " in parts[1]:
                        return parts[1].split(": ")[0]
    except FileNotFoundError:
        return None
    return None

def inject_third_voice():
    if os.path.exists(MANUAL_INSERT_FILE):
        with open(MANUAL_INSERT_FILE, "r", encoding="utf-8") as f:
            insert_text = f.read().strip()
        if insert_text:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            entry = f"{timestamp} Third Voice: {insert_text}"
            append_to_log(entry)
            with open(MANUAL_INSERT_FILE, "w", encoding="utf-8") as f:
                f.write("")

@app.route("/")
def index():
    return "Moira–Lee–Third Voice Dialogue"

@app.route("/dialogue")
def dialogue():
    try:
        inject_third_voice()
        if not os.path.exists(LOG_FILE):
            return "No dialogue yet."
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return render_template_string("<pre>{{ content }}</pre>", content=content)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
