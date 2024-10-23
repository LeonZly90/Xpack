from flask import Flask, render_template_string, request, jsonify, send_from_directory, Response
from pymongo import MongoClient
from bson import ObjectId
import os
import config  # Import the config file

# venv\Scripts\activate

app = Flask(__name__)

# MongoDB setup using config
client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
products_collection = db[config.COLLECTION_NAME]
print(db, products_collection)

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, 'images')
EXCEL_FILE = os.path.join(BASE_DIR, 'Product details by suppliers.xlsx')

app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

@app.route('/upload', methods=['POST'])
def upload_data():
    df = pd.read_excel(EXCEL_FILE)
    data = df.to_dict('records')
    products_collection.delete_many({})  # Clear existing data
    products_collection.insert_many(data)
    return jsonify({"message": "Data uploaded successfully", "count": len(data)})

@app.route('/', methods=['GET', 'POST'])
def home():
    search_result = None
    if request.method == 'POST':
        search_query = request.form.get('search').lower()
        search_result = list(products_collection.find({
            "$or": [
                {"Supplier Name": {"$regex": search_query, "$options": "i"}},
                {"Category": {"$regex": search_query, "$options": "i"}},
                {"Pump Technology": {"$regex": search_query, "$options": "i"}},
                {"Product Name": {"$regex": search_query, "$options": "i"}},
                {"Product description": {"$regex": search_query, "$options": "i"}},
                {"Dosage option": {"$regex": search_query, "$options": "i"}},
                {"Fixation/Neck finishes": {"$regex": search_query, "$options": "i"}},
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
                <td>{{ row['Supplier Name'] }}</td>
                <td>{{ row['Category'] }}</td>
                <td>{{ row['Pump Technology'] }}</td>
                <td>{{ row['Product Name'] }}</td>
                <td>{{ row['Product description'] }}</td>
                <td>{{ row['Dosage option'] }}</td>
                <td>{{ row['Fixation/Neck finishes'] }}</td>
                <td>
                    {% if row['images'] %}
                        {% for i in range(row['images']|length) %}
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
    if document and 'images' in document and len(document['images']) > image_index:
        # Get the binary image data
        image_binary = document['images'][image_index]
        # Return it as a response
        return Response(image_binary, mimetype='image/png')
    return 'Image not found', 404

if __name__ == '__main__':
    app.run(debug=True)
