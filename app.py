import os
import openai
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from your Wix site

# Get OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to search Indian Kanoon
def search_indian_kanoon(query):
    url = f"https://indiankanoon.org/search/?formInput={query}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for r in soup.select(".result_title")[:5]:  # Get top 5 results
        title = r.text.strip()
        link = "https://indiankanoon.org" + r['href']
        results.append(f"{title}: {link}")
    return results

# Function to ask GPT for summaries
def summarize_with_gpt(query, cases):
    prompt = (
        f"You are a legal research assistant. A user asked: “{query}”.\n\n"
        "Here are the top cases found:\n" +
        "\n".join(cases) +
        "\n\nFor each case, provide a short plain-English summary."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Or gpt-3.5-turbo if you prefer
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling GPT: {str(e)}"

# API endpoint to receive questions
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query") or data.get("message")
    if not query:
        return jsonify({"reply": "Please enter a legal question."})

    cases = search_indian_kanoon(query)
    if not cases:
        return jsonify({"reply": "No relevant cases found."})

    reply = summarize_with_gpt(query, cases)
    return jsonify({"reply": reply})

# Start the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
