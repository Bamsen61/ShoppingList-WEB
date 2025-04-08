import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Example: Add data to Firestore
def add_data(collection_name, document_id, data):
    try:
        db.collection(collection_name).document(document_id).set(data)
        print(f"Document {document_id} added to {collection_name} collection.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    collection_name = "users"
    document_id = "user1"
    data = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "age": 30
    }
    add_data(collection_name, document_id, data)