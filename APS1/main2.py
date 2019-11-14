from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import pymongo
import os 
from bson.objectid import ObjectId

ip = os.getenv("cloudDatabase")

# Creating database
string = "mongodb://" + ip + ":27017/"
myclient = pymongo.MongoClient(string) 
mydb = myclient["projectDatabase"]
tasks = mydb["tasks"]

app = FastAPI()

class Task(BaseModel):
    name: str
    description: str

# /task
@app.get("/task")
async def get_task():
    res = {}
    res["Values"] = []
    for i in tasks.find():
        res["Values"].append({'id': str(i["_id"]), 'name': i["name"], 'description': i["description"]})
    return res

@app.post("/task")
async def post_task(task: Task):
    dictio = {"name": task.name, "description": task.description}
    tasks.insert_one(dictio)

# /task/<id>
@app.get("/task/{id}")
async def get_task_id(id: str):
    res = {}
    res["Values"] = []
    for i in tasks.find( {"_id": ObjectId(id)} ):
        res["Values"].append({'id': str(i["_id"]), 'name': i["name"], 'description': i["description"]})
    return res

@app.put("/task/{id}")
async def put_task_id(id: str, task: Task):
    tasks.update_one( {"_id": ObjectId(id)}, {"$set": {"name": task.name, "description": task.description}})
    
    
@app.delete("/task/{id}")
async def delete_task(id: str):
    tasks.remove( {"_id": ObjectId(id)} )

# /healthcheck (only returns status 200)
@app.get("/healthcheck", status_code=200)
async def health_check():
    return