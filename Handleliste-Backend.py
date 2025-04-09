# === Python backend using Flask and Firebase Realtime Database ===

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Firebase Realtime Database setup
cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\handleliste-3bdaa-firebase-adminsdk-fbsvc-37480a5d30.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'
})
items_ref = db.reference("handleliste")

# Get items for a shop where Buy = True (case insensitive shop match)
@app.route("/items")
def get_items():
    shop = request.args.get("shop", "").lower()
    items = items_ref.get() or {}
    filtered = [dict(id=k, **v) for k, v in items.items()
                if v.get("Buy") == True and v.get("Shop", "").lower() == shop]
    return jsonify(filtered)

# Get all items
@app.route("/all-items")
def get_all_items():
    items = items_ref.get() or {}
    return jsonify([dict(id=k, **v) for k, v in items.items()])

# Add a new item
@app.route("/item/add", methods=["POST"])
def add_item():
    data = request.json
    data["Buy"] = True
    data["BuyNumber"] = 0
    data["BoughtDate"] = [None]*10
    items_ref.push(data)
    return ("", 204)

# Set Buy = True for existing item
@app.route("/item/buy", methods=["POST"])
def buy_item():
    item_id = request.json["id"]
    items_ref.child(item_id).update({"Buy": True})
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
    app.run(debug=True)
