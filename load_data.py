from pymongo import MongoClient
from bson.binary import Binary
import os

# MongoDB connection
MONGO_URI = "mongodb+srv://leonzly90:Thisismynewpwd1!@xpackcluster0.puaxv.mongodb.net/?retryWrites=true&w=majority&appName=xpackCluster0"
client = MongoClient(MONGO_URI)
db = client['xpack_db0']
products_collection = db['xpack_collection0']

# Directory containing images
images_dir = r"C:\Users\jeffz\Desktop\Projects\Xpack\images"

# Get all PNG files from the directory
image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
images_binary = []

# Read all images
for image_file in image_files:
    image_path = os.path.join(images_dir, image_file)
    print(f"Processing image: {image_file}")
    with open(image_path, 'rb') as f:
        images_binary.append(Binary(f.read()))

# Create product document with images
product_data = {
    "Supplier Name": "Aptar",
    "Category": "Fragrance",
    "Pump Technology": "Spray Pump",
    "Product Name": "InNue",
    "Product description": "Classic INUNE provides a precise spray...",
    "Dosage option": "70, 100mcl",
    "Fixation/Neck finishes": "Screw on 15, Crimp 13, 15, 17, 18, 20. Snap on 13mm, 15mm",
    "images": images_binary  # Store array of binary images
}

# Insert into MongoDB
result = products_collection.insert_one(product_data)
print(f"Inserted document with ID: {result.inserted_id}")
print(f"Processed {len(images_binary)} images")