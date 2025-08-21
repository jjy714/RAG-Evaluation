import time
from pymongo import MongoClient

def mongo_test():
    """Connects to MongoDB and inserts a test document."""
    client = None
    try:
        print("Attempting to connect to MongoDB...")
        client = MongoClient(
            host='mongodb://localhost:9017/',
            username='root',
            password='changeme',
            serverSelectionTimeoutMS=5000  # Set a timeout for the connection
        )
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful.")

        db = client.testdb
        datasets_collection = db.test_collection
        print(f"Using database 'testdb' and collection 'test_collection'.")

        test_document = {
            'upload_id': f'upload_test_{time.time()}',
            'user_id': 'user_test',
            'filename': 'test.txt',
            'data': b'test data',
            'upload_timestamp': time.time()
        }

        print("Attempting to insert a test document...")
        datasets_collection.insert_one(test_document)
        print("Test document inserted successfully.")
        return "Success"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Failed"
    finally:
        if client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    mongo_test()