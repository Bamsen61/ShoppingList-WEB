import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\handleliste-3bdaa-firebase-adminsdk-fbsvc-37480a5d30.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

def add_item(name, buy, added_by, shop, buy_number, bought_date):
  item = {
    "Name": name,
    "Buy": buy,
    "AddedBy": added_by,
    "Shop": shop,
    "BuyNumber": buy_number,
    "BoughtDate": bought_date
  }
  db.collection("handleliste").document().set(item)

def get_items():
  items = db.collection("handleliste").stream()
  return [{doc.id: doc.to_dict()} for doc in items]

def update_item(item_id, field, value):
  db.collection("handleliste").document(item_id).update({field: value})

def delete_item(item_id):
  db.collection("handleliste").document(item_id).delete()

add_item("Melk", "Yes", "Morten", "Extra", 1, "2025-03-15")

items = get_items()
for item in items:
  print(item)