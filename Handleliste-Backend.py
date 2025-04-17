# === Python backend using Flask and Firebase Realtime Database ===

from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime  # Import to get the current date
import secrets  # For generating secure tokens
from functools import wraps
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Firebase Realtime Database setup
import os

# Determine the path to the Firebase credentials file based on the environment
if os.environ.get("FLY_APP_NAME"):
    # Production environment
    cred_path = "firebase-creds.json"
else:
    # Local environment
    cred_path = "D:\\GIT\\ShoppingList-WEB\\firebase-creds.json"

cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'
})
items_ref = db.reference("handleliste")

# In-memory storage for simplicity (use a database in production)
USERS = {"Morten": "President", "Linh": "Smile1982"}  # Replace with your usernames and passwords
TOKENS = {}  # Maps tokens to usernames
TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'tokens.json')

# Load tokens from file at startup
if os.path.exists(TOKENS_FILE):
    try:
        with open(TOKENS_FILE, 'r') as f:
            TOKENS.update(json.load(f))
    except Exception as e:
        logging.error(f"Failed to load tokens from {TOKENS_FILE}: {e}")

# Helper to save tokens to file
def save_tokens():
    try:
        with open(TOKENS_FILE, 'w') as f:
            json.dump(TOKENS, f)
    except Exception as e:
        logging.error(f"Failed to save tokens to {TOKENS_FILE}: {e}")

# Automatically log in as "Morten" during local debugging
if not os.environ.get("FLY_APP_NAME"):
    @app.before_request
    def auto_login_for_debug():
        if request.endpoint not in ["static", "serve_frontend"]:
            g.debug_token = "debug-token"
            TOKENS["debug-token"] = "Morten"

# Log incoming requests
# @app.before_request
# def log_request_info():
#     logging.debug(f"Request endpoint: {request.endpoint}")
#     logging.debug(f"Request headers: {request.headers}")
#     logging.debug(f"Request data: {request.data}")

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) == password:
        # Generate a token
        token = secrets.token_hex(16)
        TOKENS[token] = username
        save_tokens()  # Persist tokens on every change
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        # Check for debug token in Flask's g (for local debug)
        if not token and hasattr(g, "debug_token"):
            token = g.debug_token
        if token not in TOKENS:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Get items for a shop where Buy = True (case insensitive shop match)
@app.route("/items")
@require_auth
def get_items():
    shop = request.args.get("shop", "").lower()
    items = items_ref.get() or {}
    filtered = [dict(id=k, **v) for k, v in items.items()
                if v.get("Buy") == True and v.get("Shop", "").lower() == shop]
    return jsonify(filtered)

# Get all items
@app.route("/all-items")
@require_auth
def get_all_items():
    items = items_ref.get() or {}
    return jsonify([dict(id=k, **v) for k, v in items.items()])

# Add a new item to the database
@app.route("/item/additemtodatabase", methods=["POST"])
def add_item():
    data = request.json
    data["Buy"] = True
    data["BuyNumber"] = 0
    data["BoughtDate"] = [None] * 10
    data["AddedBy"] = data.get("AddedBy", "Anonymous")  # Default to "Anonymous" if not provided
    items_ref.push(data)
    return ("", 204)

# Mark an item to buy
@app.route("/item/markitemtobuy", methods=["POST"])
def mark_item_to_buy():
    item_id = request.json["id"]
    items_ref.child(item_id).update({"Buy": True})
    return ("", 204)

# Mark an item as bought
@app.route("/item/markitemasbought", methods=["POST"])
def buy_item():
    item_id = request.json["id"]
    bought_by = request.json.get("BoughtBy", "Anonymous")  # Get the name of the person who bought the item

    # Retrieve the current item data
    item = items_ref.child(item_id).get()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Update the item
    bought_dates = item.get("BoughtDate", [])
    current_date = datetime.now().strftime("%Y-%m-%d")  # Get the current date in YYYY-MM-DD format
    updated_bought_dates = [current_date] + bought_dates[:9]  # Add the current date and keep only the last 10 dates

    updated_data = {
        "Buy": False,
        "BoughtBy": bought_by,
        "BoughtDate": updated_bought_dates,
        "BuyNumber": item.get("BuyNumber", 0) + 1  # Increment BuyNumber
    }

    items_ref.child(item_id).update(updated_data)
    return ("", 204)

# Set Buy = False for existing item
@app.route("/item/remove", methods=["POST"])
def remove_item():
    item_id = request.json["id"]
    items_ref.child(item_id).update({"Buy": False})
    return ("", 204)

# Delete item
@app.route("/item", methods=["DELETE"])
def delete_item():
    item_id = request.json["id"]
    items_ref.child(item_id).delete()
    return ("", 204)

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
