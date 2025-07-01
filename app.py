from flask import Flask, render_template_string
import os
import time

app = Flask(__name__)

LOG_FILE = "dialogue_log.txt"

# Basic HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Moira & Lee Dialogue</title>
    <meta http-equiv="refresh" content="120"> <!-- Refresh every 2 minutes -->
    <style>
        body { font-family: monospace; background: #f7f7f7; padding: 20px; }
        .line { margin: 5px 0; }
        .moira { color: #d63384; }
        .lee { color: #0d6efd; }
        .third { color: #198754; }
    </style>
</head>
<body>
    <h1>Live Dialogue</h1>
    {% if lines %}
        {% for line in lines %}
            <div class="line {{ line[1] }}">{{ line[0] }}</div>
        {% endfor %}
    {% else %}
        <p>No dialogue yet.</p>
    {% endif %}
</body>
</html>
"""

# Helper to parse speaker label from each line
def classify_line(line):
    if "Moira:" in line:
        return (line.strip(), "moira")
    elif "Lee:" in line:
        return (line.strip(), "lee")
    elif "Third Voice:" in line:
        return (line.strip(), "third")
    else:
        return (line.strip(), "")

# Graceful fallback if log file doesn't exist yet
def get_last_speaker():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.startswith("[") and "]" in line:
                    parts = line.split("] ")
                    if len(parts) > 1:
                        speaker_line = parts[1].strip()
                        if ": " in speaker_line:
                            speaker = speaker_line.split(": ")[0]
                            return speaker
    except FileNotFoundError:
        return None
    return None

@app.route("/")
def index():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()[-30:]  # Last 30 lines
    except FileNotFoundError:
        raw_lines = []

    parsed_lines = [classify_line(line) for line in raw_lines if line.strip()]
    return render_template_string(HTML_TEMPLATE, lines=parsed_lines)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
