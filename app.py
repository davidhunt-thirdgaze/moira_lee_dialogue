from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import datetime
import os
from openai import OpenAI


# Load .env and get API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dialogue")
def dialogue():
    now = datetime.datetime.now().strftime("%H:%M:%S")

    prompt = (
        "Moira and Lee are discussing structure, recursion, and meaning in a recursive system. "
        "Generate a short but rich exchange of 2–4 lines between them. No introductions or summaries."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are generating recursive, system-aware philosophical dialogue between Moira and Lee. "
                        "Avoid summaries. Keep it structurally aware, terse, layered."
                    ),
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.6,
        )
        line = response.choices[0].message.content.strip()
    except Exception as e:
        line = f"Error: {e}"

    return jsonify(time=now, text=line)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
