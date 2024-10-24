from flask import Flask, render_template_string, request, jsonify, send_from_directory, Response
from pymongo import MongoClient
from bson import ObjectId
import os
import config  # Import the config file
import pandas as pd
from load_data import load_data

# venv\Scripts\activate

app = Flask(__name__)

# MongoDB setup using config
client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
products_collection = db[config.COLLECTION_NAME]
print(db, products_collection)

@app.route('/upload', methods=['POST'])
def upload_data():
    products_collection.delete_many({})  # Clear existing data
    load_data()

@app.route('/', methods=['GET', 'POST'])
def home():
    search_result = None
    if request.method == 'POST':
        search_query = request.form.get('search').lower()
        search_result = list(products_collection.find({
            "$or": [
                {"SupplierName": {"$regex": search_query, "$options": "i"}},
                {"Category": {"$regex": search_query, "$options": "i"}},
                {"PumpTechnology": {"$regex": search_query, "$options": "i"}},
                {"ProductName": {"$regex": search_query, "$options": "i"}},
                {"ProductDescription": {"$regex": search_query, "$options": "i"}},
                {"DosageOption": {"$regex": search_query, "$options": "i"}},
                {"FixationNeckFinish": {"$regex": search_query, "$options": "i"}},
            ]
        }))
        # Add debug print
        print(f"Found {len(search_result)} results")
        for doc in search_result:
            print(f"Document: {doc}")

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>X-Pack Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            form { margin-bottom: 20px; }
            input[type="text"] { padding: 5px; width: 200px; }
            input[type="submit"] { padding: 5px 10px; }
            #result { color: #007bff; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .image-cell { cursor: pointer; color: blue; text-decoration: underline; }
            #imageModal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9); }
            #modalImage { margin: auto; display: block; width: 80%; max-width: 700px; }
            .close { color: #f1f1f1; font-size: 40px; font-weight: bold; position: absolute; right: 35px; top: 15px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Welcome to X-Pack Demo</h1>
        <form method="post">
            <input type="text" name="search" placeholder="Enter search term">
            <input type="submit" value="Search">
        </form>
        {% if search_result %}
        <table>
            <tr>
                <th>Supplier Name</th>
                <th>Category</th>
                <th>Pump Technology</th>
                <th>Product Name</th>
                <th>Product Description</th>
                <th>Dosage Option</th>
                <th>Fixation/Neck Finishes</th>
                <th>Images</th>
            </tr>
            {% for row in search_result %}
            <tr>
                <td>{{ row['SupplierName'] }}</td>
                <td>{{ row['Category'] }}</td>
                <td>{{ row['PumpTechnology'] }}</td>
                <td>{{ row['ProductName'] }}</td>
                <td>{{ row['ProductDescription'] }}</td>
                <td>{{ row['DosageOption'] }}</td>
                <td>{{ row['FixationNeckFinish'] }}</td>
                <td>
                    {% if row['Images'] %}
                        {% for i in range(row['Images']|length) %}
                            <span class="image-cell" onclick="showImage('{{ row['_id'] }}/{{ i }}')">View Image {{ i + 1 }}</span><br>
                        {% endfor %}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}

        <div id="imageModal">
            <span class="close" onclick="closeModal()">&times;</span>
            <img id="modalImage">
        </div>

        <script>
            function showImage(imageId) {
                var modal = document.getElementById('imageModal');
                var modalImg = document.getElementById('modalImage');
                modal.style.display = "block";
                modalImg.src = "/image/" + imageId;
            }

            function closeModal() {
                document.getElementById('imageModal').style.display = "none";
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, search_result=search_result)

@app.route('/image/<object_id>/<int:image_index>')
def serve_image(object_id, image_index):
    # Find the document
    document = products_collection.find_one({'_id': ObjectId(object_id)})
    if document and 'Images' in document and len(document['Images']) > image_index:
        # Get the binary image data
        image_binary = document['Images'][image_index]
        # Return it as a response
        return Response(image_binary, mimetype='image/png')
    return 'Image not found', 404

if __name__ == '__main__':
    upload_data()
    app.run(debug=True)
