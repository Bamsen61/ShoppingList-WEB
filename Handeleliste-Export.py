# Handeleliste-Export
# Eksporterer varer fra Firebase til CSV

import csv
import os
import sys
import firebase_admin
from firebase_admin import credentials, db
sys.path.append(os.path.dirname(__file__))

cred = credentials.Certificate("D:\\GIT\\ShoppingList-WEB\\firebase-creds.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://handleliste-3bdaa-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference('handleliste')

CSV_PATH = r"C:\Users\morte\OneDrive\Desktop\Handleliste-Export.csv"

FIELDNAMES = [
    "ID", "Name", "Shop", "AddedBy", "BoughtBy", "BuyNumber", "Buy"
] + [f"BoughtDate {i}" for i in range(10)]

def main():
    all_items = ref.get()
    if not all_items:
        print("No data found in handleliste.")
        return
    with open(CSV_PATH, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for key, row in all_items.items():
            bought_dates = row.get("BoughtDate", [])
            bought_dates = bought_dates if isinstance(bought_dates, list) else []
            csv_row = {
                "ID": key,
                "Name": row.get("Name", ""),
                "Shop": row.get("Shop", ""),
                "AddedBy": row.get("AddedBy", ""),
                "BoughtBy": row.get("BoughtBy", ""),
                "BuyNumber": row.get("BuyNumber", 0),
                "Buy": row.get("Buy", False),
            }
            for i in range(10):
                csv_row[f"BoughtDate {i}"] = bought_dates[i] if i < len(bought_dates) else ""
            writer.writerow(csv_row)
    print(f"Exported {len(all_items)} records to {CSV_PATH}")

if __name__ == "__main__":
    main()
