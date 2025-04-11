# === Python backend using Flask and Firebase Realtime Database ===

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime  # Import to get the current date
import secrets  # For generating secure tokens
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Firebase Realtime Database setup
# cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\firebase-creds.json") # Local path to your Firebase credentials file
cred = credentials.Certificate("firebase-creds.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'
})
items_ref = db.reference("handleliste")

# In-memory storage for simplicity (use a database in production)
USERS = {"Morten": "President", "Linh": "Smile1982"}  # Replace with your usernames and passwords
TOKENS = {}  # Maps tokens to usernames

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
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
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

# Add a new item
@app.route("/item/add", methods=["POST"])
def add_item():
    data = request.json
    data["Buy"] = True
    data["BuyNumber"] = 0
    data["BoughtDate"] = [None] * 10
    data["AddedBy"] = data.get("AddedBy", "Anonymous")  # Default to "Anonymous" if not provided
    items_ref.push(data)
    return ("", 204)

# Set Buy = True for existing item
@app.route("/item/buy", methods=["POST"])
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
