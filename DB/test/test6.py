import time
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
import pandas as pd

# --- Configuration ---
# IMPORTANT: Use 'localhost' if running this script from your host machine.
# If running this script from another Docker container on the same network,
# use the service name (e.g., 'mongodb' or 'postgres').
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')

MONGO_URI = f"mongodb://{MONGO_HOST}:27017/"
POSTGRES_URI = f"dbname='testdb' user='testuser' password='testpassword' host='{POSTGRES_HOST}'"

NUM_THREADS = 50
WRITES_PER_THREAD = 1000
TOTAL_WRITES = NUM_THREADS * WRITES_PER_THREAD
NUM_USERS = 50 # Each thread will simulate one user uploading the dataset
# --- Worker Functions (These remain synchronous and blocking) ---

def mongo_worker(worker_id):
    """
    Connects to MongoDB and inserts a batch of documents.
    Each thread gets its own MongoClient instance. This function is blocking.
    """
    client = None
    try:
        client = MongoClient(
            # host='host.docker.internal', 
            host='mongodb://localhost:9017/', 
            # port=9017, 
            username='root',
            password='changeme',
        )   

        db = client.testdb
        dataset_collection = db.dataset_collection
        
        csv_file_path = './response_merged_output.csv' # Replace with your CSV file path
        df = pd.read_csv(csv_file_path)
        data = df.to_dict(orient='records') # Convert DataFrame to a list of dictionaries
        dataset_document = {
            'upload_id': f'upload_{worker_id}_{time.time()}',
            'user_id': f'user_{worker_id}',
            'filename': os.path.basename(csv_file_path),
            'data': data,
            'upload_timestamp': time.time()
        }
        dataset_collection.insert_one(dataset_document)
        return f"Mongo Worker {worker_id}: Uploaded {len(dataset_document)} records."
    except Exception as e:
        return f"Mongo Worker {worker_id} failed: {e}"
    finally:
        if client:
            client.close()

# def postgres_worker(worker_id):
#     """
#     Connects to PostgreSQL and inserts a batch of rows.
#     Each thread gets its own connection. This function is blocking.
#     """
#     conn = None
#     try:
#         conn = psycopg2.connect(POSTGRES_URI)
#         cur = conn.cursor()

#         # This check is not thread-safe and might run multiple times,
#         # but CREATE TABLE IF NOT EXISTS handles this gracefully.
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS logs (
#                 id SERIAL PRIMARY KEY,
#                 log_data JSONB
#             );
#         """)
#         conn.commit()

#         for i in range(WRITES_PER_THREAD):
#             log_entry = {
#                 'worker_id': worker_id,
#                 'message': f'Log entry {i} from worker {worker_id}',
#                 'timestamp': time.time()
#             }
#             cur.execute("INSERT INTO logs (log_data) VALUES (%s)", (Json(log_entry),))
        
#         conn.commit()
#         return f"Worker {worker_id} finished."
#     except Exception as e:
#         return f"Worker {worker_id} failed: {e}"
#     finally:
#         if conn:
#             conn.close()

# --- Async Execution Logic ---

async def run_test(target_function, db_name, csv_path='./response_merged_output.csv'):
    """
    Uses asyncio to run the synchronous worker function in a thread pool.
    """
    if not os.path.exists(csv_path):
        print(f"Error: Dataset file not found at '{csv_path}'. Please update the YOUR_CSV_PATH variable.")
        return

    print(f"\n--- Starting Dataset Upload Stress Test for {db_name} ---")
    print(f"Concurrent Users (Threads): {NUM_USERS}")
    
    start_time = time.time()
    
    loop = asyncio.get_running_loop()
    
    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        # Create a list of asyncio tasks, each running a worker in the executor
        tasks = [
            loop.run_in_executor(executor, target_function, i)
            for i in range(NUM_USERS)
        ]

        results = await asyncio.gather(*tasks)
        
        # Optionally print results for debugging
        for result in results:
            print(result)

    end_time = time.time()
    duration = end_time - start_time
    uploads_per_second = NUM_USERS / duration

    print(f"--- Test for {db_name} Finished ---")
    print(f"Total time to upload {NUM_USERS} datasets: {duration:.2f} seconds")
    print(f"Uploads per second: {uploads_per_second:.2f}")


async def main():
    """Main async function to run the tests sequentially."""
    await run_test(mongo_worker, "MongoDB")
    # await run_test(postgres_worker, "PostgreSQL")


if __name__ == "__main__":
    # Use asyncio.run() to start the async event loop
    asyncio.run(main())
