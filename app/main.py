from fastapi import FastAPI
from .database import create_db_and_tables
app = FastAPI()


@app.get('/')
def hello_world():
    return 'Hello, World!'

def add (a: int, b:int) -> int:
	return a+b