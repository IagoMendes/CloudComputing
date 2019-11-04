from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
test = dict()

class Task(BaseModel):
    name: str
    description: str

# /task
@app.get("/task")
async def get_task():
    return test

@app.post("/task")
async def post_task(task: Task):
    test[len(test.keys())] = task

# /task/<id>
@app.get("/task/{id}")
async def get_task_id(id: int):
    return test.get(id)

@app.put("/task/{id}")
async def put_task_id(id: int, task: Task):
    if id in test.keys():
        test[id] = task
    else:
        raise HTTPException(status_code=404, detail='Task not found')
    
@app.delete("/task/{id}")
async def delete_task(id: int):
    if id in test.keys():
        test.pop(id)
    else:
        raise HTTPException(status_code=404, detail='Unable to delete, task not found')

# /healthcheck (only returns status 200)
@app.get("/healthcheck")
async def health_check():
    raise HTTPException(status_code=200)