from flask import Flask, render_template_string
import os
import openai
import time

app = Flask(__name__)

# Set your OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

LOG_FILE = "dialogue_log.txt"
SEED_FILE = "seed_material.txt"
MAX_HISTORY_LINES = 10

# -------------------------
# Utility Functions
# -------------------------

def read_seed():
    if os.path.exists(SEED_FILE):
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def read_history():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def write_line_to_history(line):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    full_line = f"{timestamp} {line}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_line + "\n")

def get_last_speaker(history):
    lines = history.splitlines()
    if not lines:
        return "Moira"  # default if no previous speaker
    last_line = lines[-1]
    if "Lee:" in last_line:
        return "Lee"
    elif "Moira:" in last_line:
        return "Moira"
    else:
        return "Moira"  # fallback

def generate_next_line(seed, history, speaker):
    full_prompt = f"{seed}\n\nRecent dialogue:\n{history}\n\nNext line by {speaker}:"
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # or "gpt-4-turbo" if you're using it
        messages=[
            {"role": "system", "content": seed},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=100,
        temperature=0.8
    )
    content = response['choices'][0]['message']['content'].strip()
    return f"{speaker}: {content}"

def alternate_speaker(current):
    return "Lee" if current == "Moira" else "Moira"

# -------------------------
# Dialogue Update Logic
# -------------------------

def update_dialogue():
    seed = read_seed()
    history = read_history()
    current_speaker = alternate_speaker(get_last_speaker(history))
    new_line = generate_next_line(seed, history, current_speaker)
    write_line_to_history(new_line)

# -------------------------
# Flask Routes
# -------------------------

@app.route("/")
def index():
    return render_template_string("""
        <h2>Moira–Lee Dialogue (Live Log)</h2>
        <pre style="white-space: pre-wrap;">{{ history }}</pre>
        <p><a href="/dialogue">Refresh Dialogue</a></p>
    """, history=read_history())

@app.route("/dialogue")
def dialogue():
    try:
        update_dialogue()
        return render_template_string("""
            <h2>Moira–Lee Dialogue (Updated)</h2>
            <pre style="white-space: pre-wrap;">{{ history }}</pre>
            <p><a href="/">Back</a></p>
        """, history=read_history())
    except Exception as e:
        return f"<b>Error:</b><br><pre>{str(e)}</pre>"

# -------------------------
# Run (for local testing)
# -------------------------

if __name__ == "__main__":
    app.run(debug=True, port=10000)
