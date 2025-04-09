import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime  # Import to get today's date

# Initialize Firebase Admin SDK
cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\handleliste-3bdaa-firebase-adminsdk-fbsvc-37480a5d30.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'  # Replace with your Realtime Database URL
})

# Connect to Realtime Database
ref = db.reference('handleliste')  # Root reference for the "handleliste" collection

def add_item(name, added_by, shop, buy="Yes", buy_number=0, bought_dates=None):
    """
    Adds an item to the database.

    :param name: Name of the item
    :param added_by: Who added the item
    :param shop: Shop where the item is bought
    :param buy: Whether the item should be bought
    :param buy_number: Quantity to buy
    :param bought_dates: List of dates when the item was bought
    """
    if bought_dates is None:
      bought_dates = []  # Default to an empty list if not provided
    item = {
        "Name": name,
        "Buy": buy,
        "AddedBy": added_by,
        "Shop": shop,
        "BuyNumber": buy_number,
        "BoughtDates": bought_dates  # Store as an array of dates
    }
    ref.push(item)  # Push a new item to the database

def get_items():
    items = ref.get()  # Retrieve all items
    return items if items else {}

def update_item(item_id, field, value):
    ref.child(item_id).update({field: value})  # Update a specific field of an item

def delete_item(item_id):
    ref.child(item_id).delete()  # Delete an item by its ID

def get_items_by_shop(shop_name):
    """
    Retrieves all items where the 'Shop' field matches the given shop name.

    :param shop_name: The name of the shop to filter by
    :return: A dictionary of items matching the shop name
    """
    items = ref.order_by_child('Shop').equal_to(shop_name).get()
    return items if items else {}

def get_items_by_person(AddedBy):
    items = ref.order_by_child('AddedBy').equal_to(AddedBy).get()
    return items if items else {}

def update_item_by_name_and_shop(name, shop):
    """
    Updates an item based on its 'Name' and 'Shop'.
    Sets 'Buy' to 'No', increments 'BuyNumber' by 1, and adds today's date to 'BoughtDates'.

    :param name: The name of the item to update
    :param shop: The shop of the item to update
    """
    # Query items by Name and Shop
    items = ref.order_by_child('Name').equal_to(name).get()
    for item_id, item_data in items.items():
        if item_data.get('Shop') == shop:
            # Update the item
            updated_bought_dates = [datetime.now().strftime("%Y-%m-%d")] + item_data.get('BoughtDates', [])
            ref.child(item_id).update({
                "Buy": "No",
                "BuyNumber": item_data.get("BuyNumber", 0) + 1,
                "BoughtDates": updated_bought_dates
            })
            print(f"Updated item: {item_id} => {item_data}")
            return
    print(f"No item found with Name='{name}' and Shop='{shop}'")

# add_item(name="Head and Shoulders",added_by="Linh", shop="Meny") 

update_item_by_name_and_shop(name="Head and Shoulders", shop="Normal")  # Example usage

# extra_items = get_items_by_shop("Meny")
extra_items = get_items_by_person("Linh")
for item_id, item_data in extra_items.items():
    print(f"{item_id} => {item_data}")

exit(0)  # Exit the script if needed

# Example usage
try:
    # Example with an array of ten dates
    add_item(
        name="Melk", 
        buy="Yes", 
        added_by="Morten", 
        shop="Extra", 
        buy_number=1, 
        bought_dates=["2025-03-15", "2025-03-16", "2025-03-17", "2025-03-18", "2025-03-19",
                      "2025-03-20", "2025-03-21", "2025-03-22", "2025-03-23", "2025-03-24"]
    )
    items = get_items()
    for item_id, item_data in items.items():
        print(f"{item_id} => {item_data}")
    
    # Retrieve items where "Shop" is "Extra"
    extra_items = get_items_by_shop("Extra")
    for item_id, item_data in extra_items.items():
        print(f"{item_id} => {item_data}")
except Exception as e:
    print(f"Error interacting with Realtime Database: {e}")