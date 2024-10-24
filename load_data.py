from pymongo import MongoClient
from bson.binary import Binary
import pandas as pd
import os
import config

def load_data():
    # MongoDB connection
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    products_collection = db[config.COLLECTION_NAME]

    # Directory
    images_dir = os.path.join(config.BASE_DIR, "image")
    text_dir = os.path.join(config.BASE_DIR, "text")

    # Get suppliers (sub dir)
    suppliers = [name for name in os.listdir(text_dir)
                if os.path.isdir(os.path.join(text_dir, name))]

    # Upload info to DB by supplier
    for supplier in suppliers:
        # Create product document with images
        products = pd.read_csv(os.path.join(text_dir, supplier, supplier + "-products.csv")).to_dict(orient='records')
        
        for product in products:
            # Get all PNG files from the directory
            image_files = [f for f in os.listdir(os.path.join(images_dir, supplier)) if f.startswith(product["ImageName"])]
            image_dict = {}

            # Read all images
            for image_file in image_files:
                image_path = os.path.join(images_dir, supplier, image_file)
                print(f"Processing image: {image_file}")
                with open(image_path, 'rb') as f:
                    image_dict[image_file] = Binary(f.read())

            product["Images"] = image_dict

            # Insert into MongoDB
            result = products_collection.insert_one(product)
            print(f"Inserted document with ID: {result.inserted_id}")
            print(f"Processed {len(image_dict)} images")