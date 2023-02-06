from fastapi import FastAPI, HTTPException, Body
from datetime import date
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import urllib
load_dotenv('.env')

DATABASE_NAME = "exceed01"
COLLECTION_NAME = "hotel_reservation"
username = os.getenv("user")
password = urllib.parse.quote(os.getenv('password'))
MONGO_DB_URL = f"mongodb://{username}:{password}@mongo.exceed19.online"
MONGO_DB_PORT = 8443


class Reservation(BaseModel):
    name : str
    start_date: date
    end_date: date
    room_id: int


client = MongoClient(f"{MONGO_DB_URL}:{MONGO_DB_PORT}/?authMechanism=DEFAULT")

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]

app = FastAPI()


def room_avaliable(room_id: int, start_date: str, end_date: str):
    query={"room_id": room_id,
           "$or": 
                [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
                 {"$and": [{"start_date": {"$lte": end_date}}, {"end_date": {"$gte": end_date}}]},
                 {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
            }
    
    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0


@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name:str):
    pass

@app.get("/reservation/by-room/{room_id}")
def get_reservation_by_room(room_id: int):
    pass

@app.post("/reservation")
def reserve(reservation : Reservation):
    pass

@app.put("/reservation/update")
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    pass

@app.delete("/reservation/delete")
def cancel_reservation(reservation: Reservation):
    pass