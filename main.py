from typing import Union
from controllers.controller import Controller
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional
import threading
import time

load_dotenv()
app = FastAPI()
controller = Controller()
def run_scheduler():
  while True:
    controller.check_task()
    time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
@app.get("/")
def read_root():
  return controller.get_tasks

class TaskCreateRQ(BaseModel):
  title: str
  desc: str
  date: datetime
  completed: bool
  priority: int
  dependencies: Optional[List[str]] = []
  
class TaskUpdate(BaseModel):
  task_id: str
  title: str | None = None
  desc: str | None = None
  completed: bool | None = None
  date: datetime | None = None
  priority: int | None = None

@app.post("/items")
def create_item(request: TaskCreateRQ):
  try:
    dependencies = [ObjectId(dep) for dep in request.dependencies or []]
    completed = bool(request.completed) if request.completed is not None else False
  except:
    raise HTTPException(status_code=422, detail="objectId invalid")
  return controller.create_task(request.title, request.desc, request.date, completed, request.priority, dependencies)
@app.get("/items")
def read_item(page: int = 1, limit: int = 5):
  return controller.get_task(page, limit)
@app.patch("/items")
def update_item(request: TaskUpdate):
  try: 
    task_id = ObjectId(request.task_id)
    update_data = {k: v for k, v in request.dict(exclude={"task_id"}).items() if v is not None}
    if not update_data:
      raise HTTPException(status_code=400, detail="No valid fields to update")
  except:
    raise HTTPException(status_code=422, detail="data invalid")
  return controller.update_task(task_id, update_data)
@app.delete("/items")
def delete_item(__task_id: str):
  try:
    task_id = ObjectId(__task_id)
  except:
    raise HTTPException(status_code=422, detail="data invalid")
  return controller.delete_task(task_id)
@app.post("/item/dependency")
def create_dependency(__task_id: str, __dep_id: str):
  try:
    task_id = ObjectId(__task_id)
    dep_id = ObjectId(__dep_id)
    print(task_id, dep_id)
  except:
    raise HTTPException(status_code=422, detail="data invalid")
  return controller.create_dependency(task_id=task_id, dep_id=dep_id)
@app.delete("/item/dependency")
def delete_dependency(__task_id: str, __dep_id: str):
  try:
    task_id = ObjectId(__task_id)
    dep_id = ObjectId(__dep_id)
  except:
    raise HTTPException(status_code=422, detail="data invalid")
  return controller.delete_dependency(task_id, dep_id)
@app.get("/item/dependency")
def get_dependency(__task_id: str):
  try:
    print(__task_id)
    task_id = ObjectId(__task_id)
    print(task_id)
    # return {"message": "success"
  
  except:
    raise HTTPException(status_code=422, detail="data invalid")
  
  datas = []
  controller.get_dependency(task_id=task_id, checkID={}, datas=datas)
  return datas
