import os
import time
from flask import Flask, render_template, request, redirect
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Load seed memory
with open("seed_material.txt", "r", encoding="utf-8") as f:
    seed_memory = f.read().strip()

# Initialize dialogue log
log_path = "dialogue_log.txt"
if not os.path.exists(log_path):
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("[SYSTEM SEED]\n" + seed_memory + "\n\n")

# Read log from file
def read_log():
    # Read and append from third_voice_insert.txt if not empty
    insert_path = "third_voice_insert.txt"
    if os.path.exists(insert_path):
        with open(insert_path, "r", encoding="utf-8") as f:
            insert_content = f.read().strip()
        if insert_content:
            timestamp = time.strftime("[%H:%M:%S]")
            formatted = f"{timestamp} Third Voice: {insert_content}"
            append_to_log(formatted)
            # Clear the file so it's not reused
            open(insert_path, "w", encoding="utf-8").close()

    with open(log_path, "r", encoding="utf-8") as f:
        return f.read()


# Append to log file
def append_to_log(text):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Clean speaker names
def format_name(name):
    return name.replace("*", "").strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            timestamp = time.strftime("[%H:%M:%S]")
            entry = f"{timestamp} You: {user_input}\n"
            append_to_log(entry)
    log = read_log()
    return render_template("index.html", log=log)

@app.route("/dialogue")
def get_dialogue():
    log = read_log()
    last_generation_time_file = "last_generation.txt"

    # Read last time from file
    try:
        with open(last_generation_time_file, "r") as f:
            last_time = float(f.read())
    except FileNotFoundError:
        last_time = 0

    current_time = time.time()
    if current_time - last_time >= 2 * 60 * 60:  # Every 2 hours
        with open(last_generation_time_file, "w") as f:
            f.write(str(current_time))

        messages = [
            {"role": "system", "content": seed_memory},
            {"role": "user", "content": read_log()}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()

            timestamp = time.strftime("[%H:%M:%S]")
            formatted = f"{timestamp} {content}"
            append_to_log(formatted)

        except Exception as e:
            append_to_log(f"[ERROR] {e}")

    return log

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
