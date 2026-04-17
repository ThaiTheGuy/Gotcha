from flask import Flask, render_template, request
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
client = Anthropic()

def analyze_lease(text):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a tenant rights expert analyzing a rental lease agreement.

Analyze the following lease text and identify clauses that are suspicious, unfair, or potentially illegal.

For each flagged clause return a JSON array like this:
[
  {{
    "clause": "exact text of the clause",
    "label": "one of: Potentially Illegal / Landlord Favored / Unusual Fee / Auto-Renewal Risk / Standard Clause",
    "explanation": "plain English explanation of why this is a concern"
  }}
]

Return ONLY the JSON array, no extra text, no markdown, no code blocks. Just the raw JSON array.

Lease text:
{text}"""
            }
        ]
    )
    raw = response.content[0].text.strip()
    print("RAW RESPONSE:", raw)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    lease_text = ""
    if request.method == "POST":
        lease_text = request.form.get("lease_text", "")
        if lease_text.strip():
            try:
                raw = analyze_lease(lease_text)
                results = json.loads(raw)
            except Exception as e:
                error = f"Something went wrong: {str(e)}"
    return render_template("index.html", results=results, error=error, lease_text=lease_text)

if __name__ == "__main__":
    app.run(debug=True)