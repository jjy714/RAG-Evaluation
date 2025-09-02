import logging
import functools
from pathlib import Path
from typing import Literal
import asyncio
import requests
import httpx
import json


FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Decorator:

    def __init__(
        self,
        num_output: int,
        eval_system_api: Literal["/DB", "/UI"],
        log_path: str = "RAG_system.log",
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
    ):
        # ----- LOG INIT -----
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger(log_path)
        self.logger.setLevel(numeric_level)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_dir / log_path)
            formatter = logging.Formatter(FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.info(f"{'='*10} Logger Initialized {'='*10}")

        # ----- PARAMS -----
        self.num_output = num_output
        self.eval_system_api = eval_system_api
        

    # ----- logging func -----
    def log_task(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"Starting task: '{func.__name__}'...")
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"Finished task: '{func.__name__}' successfully.")
                return result
            except Exception as e:
                self.logger.error(f"Error in task '{func.__name__}': {e}", exc_info=True)
                raise
        return wrapper

    # ----- data creator -----
    async def data_creator(self, func):
        """
        Takes the Raw dataset
            1. From UI
            2. From DB
            
        Makes the Benchmark dataset
            1. Insert RAG Outputs
            
        response -> a single row of data 
            ex) query, retrieval documents name, retrieval documents content, 
                target documents name, target documents content
            ex2) query, retrieval documents name, retrieval documents content, 
                target answer
        
        Sends to EVAL
        
        
        """
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            print(f"\n[Data Sender]: Preparing to create data from '{func.__name__}'...")
            asyncio.sleep(2)
            self.logger.info(f"Sending data from '{func.__name__}': {data_to_send}")
            async with httpx.AsyncClient() as client:
                data_to_send = func(*args, **kwargs)
                try: 
                    response = await client.post(self.eval_system_api, data_to_send)
                    response.raise_for_status() 
                    yield {"status": "success", "data": response.json()}

                except ConnectionError as ce: 
                    self.logger.error(f"Network error on attempt for '{func.__name__}': {ce}")
                    yield {"status": "error",  "message": str(ce)}
                except Exception as e: 
                    self.logger.error(f"An unexpected error occurred on attempt for '{func.__name__}': {e}", exc_info=True)
                    yield {"status": "error", "message": str(e)}
            print("[Data Sender]: Data sent successfully!")
            return data_to_send
        return wrapper
    
    # ----- data post -----
    async def data_sender(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            print(f"\n[Data Sender]: Preparing to send data from '{func.__name__}'...")
            async for _ in range(self.num_output):
                data_to_send = func(*args, **kwargs)
                response = await requests.post(self.eval_system_api, data_to_send)
            print(f"[Data Sender]: Data to send: {data_to_send}")
            self.logger.info(f"Sending data from '{func.__name__}': {data_to_send}")
            print("[Data Sender]: Data sent successfully!")
            return data_to_send
        return wrapper


# ----- INIT -----
decorators = Decorator(
    log_path="data_pipeline.log",
    log_level="INFO"
    )


# ----- EXAMPLE -----
@decorators.data_sender
@decorators.log_task
def process_document(doc_name: str):
    """Processes a document and returns structured data."""
    print(f"  (Inside function: Processing '{doc_name}')")
    return {"document": doc_name, "status": "processed", "pages": 15}

processed_data = process_document("annual_report_2025.pdf")

print(f"\nFinal output received: {processed_data}")
