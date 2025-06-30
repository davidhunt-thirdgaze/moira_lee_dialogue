import os
import time
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

# Load .env for API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Load initial seed memory from file
with open("seed_material.txt", "r", encoding="utf-8") as f:
    seed_memory = f.read().strip()

# Paths
log_path = "dialogue_log.txt"
manual_insert_path = "third_voice_insert.txt"
last_generation_time_file = "last_generation.txt"

# Create initial log file if it doesn't exist
if not os.path.exists(log_path):
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("[SYSTEM SEED]\n" + seed_memory + "\n\n")

# Append a line to the dialogue log
def append_to_log(text):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Inject manual Third Voice input (with full timestamp)
def inject_third_voice():
    if os.path.exists(manual_insert_path):
        with open(manual_insert_path, "r", encoding="utf-8") as f:
            insert_text = f.read().strip()
        if insert_text:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            formatted = f"{timestamp} Third Voice: {insert_text}"
            append_to_log(formatted)
            with open(manual_insert_path, "w", encoding="utf-8") as f:
                f.write("")  # Clear after injecting

# Read the full dialogue log
def read_log():
    with open(log_path, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/", methods=["GET", "POST"])
def index():
    inject_third_voice()
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            append_to_log(f"{timestamp} You: {user_input}")
    log = read_log()
    return render_template("index.html", log=log)

@app.route("/dialogue")
def get_dialogue():
    inject_third_voice()
    log = read_log()

    try:
        with open(last_generation_time_file, "r") as f:
            last_time = float(f.read())
    except FileNotFoundError:
        last_time = 0

    current_time = time.time()
    if current_time - last_time >= 2 * 60 * 60:
        with open(last_generation_time_file, "w") as f:
            f.write(str(current_time))

        messages = [
            {"role": "system", "content": seed_memory},
            {"role": "user", "content": log}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            append_to_log(f"{timestamp} {content}")
        except Exception as e:
            append_to_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {e}")

    return read_log()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
