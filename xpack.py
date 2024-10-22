#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
print(sys.executable)
print(sys.path)

# This example shows a basic structure of a demo website for X-Pack using Python (Flask) for the backend and React for the frontend.

# --- Backend (Python with Flask) --- #
# Install required packages: Flask, flask-cors, pymongo
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure

# Create a Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['xpack']

# Define collections for Supplier and Product
suppliers_collection = db['suppliers']
products_collection = db['products']

def init_db():
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful")
        
        # Initialize with some data if collections are empty
        if suppliers_collection.count_documents({}) == 0:
            suppliers_collection.insert_many([
                {"name": "Supplier A"},
                {"name": "Supplier B"}
            ])
        
        if products_collection.count_documents({}) == 0:
            products_collection.insert_many([
                {"name": "Product 1", "category": "Electronics"},
                {"name": "Product 2", "category": "Clothing"}
            ])
        
    except ConnectionFailure:
        print("MongoDB connection failed")

# Define backend routes
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = list(suppliers_collection.find())
    for supplier in suppliers:
        supplier['_id'] = str(supplier['_id'])
    return jsonify(suppliers)

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = {'category': category} if category else {}
    products = list(products_collection.find(query))
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products)

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
