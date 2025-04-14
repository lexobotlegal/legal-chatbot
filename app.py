from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows it to talk to your website

# This function does the searching
def search_indian_kanoon(query):
    url = f"https://indiankanoon.org/search/?formInput={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for result in soup.select(".result_title"):
        title = result.text.strip()
        link = "https://indiankanoon.org" + result['href']
        results.append({"title": title, "link": link})

    return results[:5]  # Top 5 results

# This is where the chatbot listens
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("query")
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    results = search_indian_kanoon(user_input)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

