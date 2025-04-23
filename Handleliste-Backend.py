# === Python backend using Flask and Firebase Realtime Database ===

from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta, timezone  # Add timezone import
import secrets  # For generating secure tokens
from functools import wraps
import os
import logging
import json
import jwt  # PyJWT for JWT tokens
import string

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

JWT_SECRET = os.environ.get("JWT_SECRET", "qKGCaoPlnk0ZGOr")
JWT_ALGORITHM = "HS256"
JWT_EXP_DAYS = 300

# Generate a global random string of 5 lowercase letters
def _generate_state_string():
    return ''.join(secrets.choice(string.ascii_lowercase) for _ in range(5))

STATE_STRING = _generate_state_string()

# Automatically log in as "Morten" during local debugging
if not os.environ.get("FLY_APP_NAME"):
    @app.before_request
    def auto_login_for_debug():
        if request.endpoint not in ["static", "serve_frontend"]:
            g.debug_token = "debug-token"

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
        # Generate JWT token
        exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)
        payload = {
            "username": username,
            "exp": exp,
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({"token": token, "expires": int(exp.timestamp())}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        # Check for debug token in Flask's g (for local debug)
        if not token and hasattr(g, "debug_token"):
            token = g.debug_token
        if token == "debug-token":
            return f(*args, **kwargs)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # Optionally, set g.user = payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired"}), 401
        except Exception:
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
  sorted_items = sorted(
    [dict(id=k, **v) for k, v in items.items()],
    key=lambda x: x.get("Name", "")
  )
  return jsonify(sorted_items)

# Add a new item to the database
@app.route("/item/additemtodatabase", methods=["POST"])
def add_item():
    global STATE_STRING
    data = request.json
    data["Buy"] = True
    data["BuyNumber"] = 0
    data["BoughtDate"] = [None] * 10
    data["AddedBy"] = data.get("AddedBy", "Anonymous")  # Default to "Anonymous" if not provided
    items_ref.push(data)
    STATE_STRING = _generate_state_string() # Generate a new state string to triger a refresh in the frontend
    return ("", 204)

# Mark an item to buy
@app.route("/item/markitemtobuy", methods=["POST"])
def mark_item_to_buy():
    global STATE_STRING
    item_id = request.json["id"]
    items_ref.child(item_id).update({"Buy": True})
    STATE_STRING = _generate_state_string() # Generate a new state string to triger a refresh in the frontend
    return ("", 204)

# Mark an item as bought
@app.route("/item/markitemasbought", methods=["POST"])
def buy_item():
    global STATE_STRING
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
    STATE_STRING = _generate_state_string() # Generate a new state string to triger a refresh in the frontend
    return ("", 204)

# Set Buy = False for existing item
# Replaced by markitemasbought. To be removed in the future.
# @app.route("/item/remove", methods=["POST"])
# def remove_item():
#     item_id = request.json["id"]
#     items_ref.child(item_id).update({"Buy": False})
#     return ("", 204)

# Delete item
@app.route("/item", methods=["DELETE"])
def delete_item():
    item_id = request.json["id"]
    items_ref.child(item_id).delete()
    return ("", 204)

# Get a custom list for markitemtobuy: 5 by person, 5 by BuyNumber, rest alphabetically
@app.route("/itemsfor-markitemtobuy")
@require_auth
def itemsfor_markitemtobuy():
    person = request.args.get("person", "")
    items = items_ref.get() or {}
    # Only items where Buy is False
    filtered = [dict(id=k, **v) for k, v in items.items() if v.get("Buy") == False]

    # Section 1: Top 5 items added by person, sorted by BuyNumber desc
    person_items = [item for item in filtered if item.get("AddedBy", "") == person]
    person_items_sorted = sorted(person_items, key=lambda x: x.get("BuyNumber", 0), reverse=True)[:5]
    person_ids = set(item["id"] for item in person_items_sorted)

    # Section 2: Top 5 items by BuyNumber (not already included), sorted by BuyNumber desc
    not_person_items = [item for item in filtered if item["id"] not in person_ids]
    top_buynumber_items = sorted(not_person_items, key=lambda x: x.get("BuyNumber", 0), reverse=True)[:5]
    top_buynumber_ids = set(item["id"] for item in top_buynumber_items)

    # Section 3: The rest, sorted alphabetically by Name
    rest_items = [item for item in filtered if item["id"] not in person_ids and item["id"] not in top_buynumber_ids]
    rest_items_sorted = sorted(rest_items, key=lambda x: x.get("Name", ""))

    result = person_items_sorted + top_buynumber_items + rest_items_sorted
    return jsonify(result)

# Get a list of all items to buy, sorted  alphabetically by Name
@app.route("/itemstobuy")
@require_auth
def itemstobuy():
    items = items_ref.get() or {}
    filtered = [dict(id=k, **v) for k, v in items.items() if v.get("Buy") == True]
    sorted_items = sorted(filtered, key=lambda x: x.get("Name", ""))
    return jsonify(sorted_items)

@app.route("/statestring")
def get_state_string():
    return jsonify({"state": STATE_STRING})

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
