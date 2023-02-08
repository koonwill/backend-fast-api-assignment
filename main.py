from fastapi import FastAPI, HTTPException, Body
from datetime import date
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import urllib
load_dotenv('.env')

DATABASE_NAME = "exceed01"
COLLECTION_NAME = "will"
username = os.getenv("user")
password = urllib.parse.quote(os.getenv('password'))
MONGO_DB_URL = f"mongodb://{username}:{password}@mongo.exceed19.online"
MONGO_DB_PORT = 8443
DATETIME_FORMAT = "%Y-%m-%d"


class Reservation(BaseModel):
    name: str
    start_date: date
    end_date: date
    room_id: int


client = MongoClient(f"{MONGO_DB_URL}:{MONGO_DB_PORT}/?authMechanism=DEFAULT")

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]

app = FastAPI()


def room_avaliable(room_id: int, start_date: str, end_date: str):
    query = {"room_id": room_id,
             "$or":
             [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
              {"$and": [{"start_date": {"$lte": end_date}},
                        {"end_date": {"$gte": end_date}}]},
              {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
             }

    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0


@app.get("/reservation/by-name/{name}", status_code=200)
def get_reservation_by_name(name: str):
    res = collection.find({"name": name}, {'_id': False})
    return {'result': list(res)}


@app.get("/reservation/by-room/{room_id}", status_code=200)
def get_reservation_by_room(room_id: int):
    if room_id not in range(1, 11):
        raise HTTPException(400, "Room id dosen't exist")
    res = collection.find({'room_id': room_id}, {'_id': False})
    return {'result': list(res)}


@app.post("/reservation", status_code=200)
def reserve(reservation: Reservation):
    if not room_avaliable(reservation.room_id, reservation.start_date.strftime(DATETIME_FORMAT), reservation.end_date.strftime(DATETIME_FORMAT)):
        raise HTTPException(400, "This room isn't avaiable")
    if reservation.room_id not in range(1, 11):
        raise HTTPException(400, "This room dosen't exist")
    if reservation.start_date > reservation.end_date:
        raise HTTPException(400, "Reservation date is more than end date")
    collection.insert_one({
        "name": reservation.name,
        "start_date": reservation.start_date.strftime(DATETIME_FORMAT),
        "end_date": reservation.end_date.strftime(DATETIME_FORMAT),
        "room_id": reservation.room_id
    })


@app.put("/reservation/update", status_code=200)
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    if not room_avaliable(reservation.room_id, new_start_date.strftime(DATETIME_FORMAT), new_end_date.strftime(DATETIME_FORMAT)):
        raise HTTPException(400, "This room isn't avaiable")
    if reservation.room_id not in range(1, 11):
        raise HTTPException(400, "This room dosen't exist")
    if new_start_date > new_end_date:
        raise HTTPException(400, "Reservation date is more than end date")
    collection.update_one({
        "name": reservation.name,
        "start_date": reservation.start_date.strftime(DATETIME_FORMAT),
        "end_date": reservation.end_date.strftime(DATETIME_FORMAT),
        "room_id": reservation.room_id
    }, {'$set': {"start_date": new_start_date.strftime(DATETIME_FORMAT),
                 "end_date": new_end_date.strftime(DATETIME_FORMAT)}})


@app.delete("/reservation/delete", status_code=200)
def cancel_reservation(reservation: Reservation):
    try:
        collection.delete_one({
            "name": reservation.name,
            "start_date": reservation.start_date.strftime(DATETIME_FORMAT),
            "end_date": reservation.end_date.strftime(DATETIME_FORMAT),
            "room_id": reservation.room_id
        })
    except Exception:
        raise HTTPException(500, "Not found this room id")
