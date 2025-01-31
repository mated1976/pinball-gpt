from flask import Flask, request, jsonify, render_template
import json
import os
from fuzzywuzzy import process

app = Flask(__name__)

# Load pinball rules JSON
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "pinball_rules.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    pinball_rules = json.load(f)

def find_best_match(query):
    """Finds the best matching pinball machine name."""
    best_match, score = process.extractOne(query, pinball_rules.keys())

    if score >= 60:
        return best_match
    return None

def search_within_game(game_name, secondary_term):
    """Search inside the matched game’s rules for additional keywords."""
    if game_name in pinball_rules:
        response = f"<strong>{game_name} - {secondary_term.capitalize()}:</strong><br><br>"
        found = False

        for url, content in pinball_rules[game_name].items():
            if secondary_term.lower() in content.lower():
                formatted_content = content.replace("\n", "<br><br>")  # ✅ Adds an extra line break
                response += f"<strong>Source:</strong> <a href='{url}' target='_blank'>{url}</a><br>"
                response += f"<div class='response-text'>{formatted_content}</div><br><hr><br>"  # ✅ Separator
                found = True
        
        return response if found else None
    return None

@app.route("/")
def home():
    """Serve the chatbot UI."""
    return render_template("chat.html")

@app.route("/query", methods=["POST"])
def query_pinball():
    """Search for pinball rules by game name and specific keywords."""
    user_query = request.json.get("question", "").lower()
    words = user_query.split()
    best_match = find_best_match(user_query)

    if best_match:
        # Check if there’s a secondary keyword in the query
        for word in words:
            if word != best_match.lower():
                match_result = search_within_game(best_match, word)
                if match_result:
                    return jsonify({"answer": match_result})

        # If no keyword is found, return **all rules** for the matched game
        response = f"<strong>{best_match} Full Rules:</strong><br><br>"

        for url, content in pinball_rules[best_match].items():
            formatted_content = content.replace("\n", "<br><br>")  # ✅ Adds an extra line break
            response += f"<strong>Source:</strong> <a href='{url}' target='_blank'>{url}</a><br>"
            response += f"<div class='response-text'>{formatted_content}</div><br><hr><br>"  # ✅ Separator

        return jsonify({"answer": response})

    return jsonify({"answer": "I couldn't find that pinball machine. Try again!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=False)
