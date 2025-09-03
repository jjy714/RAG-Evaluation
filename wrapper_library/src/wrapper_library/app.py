
from fastapi import FastAPI
import json
app = FastAPI() 



"""
@TODO

Need to create a REQUEST & RESPONSE mechanism 

1. create endpoints.
2. create prompts

Test the basic prototype


"""

@app.post("/")
def main():
    yield {"status": 200}
    

@app.post("/data")
def receieve_data(data):
    raw_data = json.dumps(data)
    
    return