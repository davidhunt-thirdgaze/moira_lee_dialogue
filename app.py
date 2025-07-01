# Revised app.py for alternating Moira–Lee dialogue with memory

import os
import time
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# File paths
SEED_FILE = "seed_material.txt"
HISTORY_FILE = "dialogue_history.txt"
LOG_FILE = "dialogue_log.txt"
THIRD_VOICE_FILE = "third_voice_insert.txt"
LAST_GEN_FILE = "last_generation.txt"

# Load seed material
with open(SEED_FILE, "r", encoding="utf-8") as f:
    seed_memory = f.read().strip()

# Ensure initial files exist
for file_path, content in [
    (HISTORY_FILE, ""),
    (LOG_FILE, f"[SYSTEM SEED]\n{seed_memory}\n\n")
]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

# Helper functions
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def append_to_file(path, line):
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def inject_third_voice():
    if os.path.exists(THIRD_VOICE_FILE):
        content = read_file(THIRD_VOICE_FILE)
        if content:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            append_to_file(LOG_FILE, f"{timestamp} Third Voice: {content}")
            write_file(THIRD_VOICE_FILE, "")

def get_last_speaker(history):
    if "Lee:" in history.splitlines()[-1]:
        return "Lee"
    return "Moira"

def generate_next_turn(history):
    messages = [
        {"role": "system", "content": seed_memory},
        {"role": "user", "content": history}
    ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Main dialogue update function
def update_dialogue():
    inject_third_voice()
    try:
        last_time = float(read_file(LAST_GEN_FILE))
    except Exception:
        last_time = 0.0

    now = time.time()
    if now - last_time < 2 * 60 * 60:
        return  # Not time yet

    history = read_file(HISTORY_FILE)
    last_speaker = get_last_speaker(history)
    next_speaker = "Lee" if last_speaker == "Moira" else "Moira"
    next_line = generate_next_turn(history)

    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    turn = f"{timestamp} {next_speaker}: {next_line}"
    append_to_file(HISTORY_FILE, turn)
    append_to_file(LOG_FILE, turn)
    write_file(LAST_GEN_FILE, str(now))

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    inject_third_voice()
    log = read_file(LOG_FILE)
    return render_template("index.html", log=log)

@app.route("/dialogue")
def dialogue():
    update_dialogue()
    return read_file(LOG_FILE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

