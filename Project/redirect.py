from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os 
import json

ip = os.getenv("redirectIp")

address = 'http://' + ip + ':8000'
app = FastAPI()


class Task(BaseModel):
    name: str
    description: str

# /task
@app.get("/task")
async def get_task():
    a = requests.get(url = address + '/task')
    return a.json()

@app.post("/task")
async def post_task(task: Task):
    data = {"name": task.name, "description": task.description}
    requests.post(url = address + '/task', data = json.dumps(data))
    

# /task/<id>
@app.get("/task/{id}")
async def get_task_id(id: str):
    a = requests.get(url = address + '/task/' + id )
    return a.json()

@app.put("/task/{id}")
async def put_task_id(id: str, task: Task):
    data = {"name": task.name, "description": task.description}
    a = requests.put(url = address + '/task/' + id, data = json.dumps(data) )
    
    
@app.delete("/task/{id}")
async def delete_task(id: str):
    a = requests.delete(url = address + '/task/' + id )

# /healthcheck (only returns status 200)
@app.get("/healthcheck", status_code=200)
async def health_check():
    a = requests.get(url = address + '/healthcheck')