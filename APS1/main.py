from fastapi import FastAPI

app = FastAPI()

test = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False }
]

@app.get("/")
async def root():
    return {"message": "Hello World"}

# /task
@app.get("/task")
async def get_task():
    return test

@app.post("/task")
async def post_task():
    test.append({
        'id': test[len(test)-1]["id"] + 1,
        'title': u'Oh hey',
        'description': u'This is working!',
        'done': True }
    )
    return test

# /task/<id>
@app.get("/task/{id}")
async def get_task_id(id):
    res = [res for res in test if res["id"] == int(id)]
    return res

@app.put("/task/{id}")
async def put_task_id(id):
    test.append({
        'id': int(id),
        'title': u'Oh hey',
        'description': u"Working too, but with an obvious logical problem =O nevermind, it's just a test",
        'done': True }
    )
    return test

@app.delete("/task/{id}")
async def delete_task(id):
    res = [res for res in test if res["id"] == int(id)]
    test.remove(res[0])
    return test

# /healthcheck (only returns status 200)
@app.get("/healthcheck")
async def health_check():
    return 