# Handeleliste-Import
# Importer varer fra CSV til Handeleliste

import csv
import os
import sys
import firebase_admin
from firebase_admin import credentials, db
sys.path.append(os.path.dirname(__file__))

cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\firebase-creds.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'  # Replace with your Realtime Database URL
})

# Connect to Realtime Database
ref = db.reference('handleliste')  # Root reference for the "handleliste" collection


CSV_PATH = r"C:\Users\morte\OneDrive\Desktop\250421 Varer fra Keep.csv"

def parse_buynumber(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def main():
    with open(CSV_PATH, encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {
                "Name": row["Name"].strip(),
                "Shop": row["Shop"].strip(),
                "AddedBy": row["AddedBy"].strip(),
                "BuyNumber": parse_buynumber(row.get("BuyNumber", "")),
                "Buy": False
            }
            ref.push(item)
            print(f"Added record #{reader.line_num - 1} for {item['Name']}")

if __name__ == "__main__":
    main()
