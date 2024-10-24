import secret
import os

# MongoDB Configuration
MONGO_URI = f"mongodb+srv://{secret.MONGO_USER}:{secret.MONGO_PWD}@xpackcluster0.puaxv.mongodb.net/?retryWrites=true&w=majority&appName=xpackCluster0"
DB_NAME = "xpack_db0"
COLLECTION_NAME = "xpack_collection0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))