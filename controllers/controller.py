from database.database import Database
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException
import pytz
class Controller:
  def __init__(self):
    self.db = Database().get_db()
  def get_tasks(self):
    return list(self.db["tasks"].find())
  def create_task(self, title: str, desc: str, date: datetime,completed: bool, priority: int, dependencies: list):
    collection = self.db["tasks"]
    valid_dependencies = []
    if dependencies:
      for dep_id in dependencies:
        if not collection.find_one({"_id": dep_id}):
          raise HTTPException(status_code=404, detail=f"Dependency Task {dep_id} not found")
        valid_dependencies.append(dep_id)
    result = self.db["tasks"].insert_one({"title": title, "description": desc, "date": date, "completed": completed, "priority": priority, "dependencies": valid_dependencies})
    return str(result.inserted_id)
  def get_task(self, page: int, limit: int):
    offset = (page - 1)*limit
    collection = self.db["tasks"]
    total_tasks = collection.count_documents({})
    total_pages = (total_tasks + limit -1)//limit
    datas = list(collection.find().skip(offset).limit(limit))
    for item in datas:
      item["_id"] = str(item["_id"])
    return {
      "datas": datas,
      "total_pages": total_pages
    }
  def update_task(self, task_id: ObjectId, update_data: dict):
    collection = self.db["tasks"]
    task = collection.find_one({"_id": task_id})
    if not task:
      raise HTTPException(status_code=404, detail="Task not find")
    result = collection.update_one(
      {"_id": task_id},
      {"$set": update_data}
    )
    return {
      "message": "success"
    }
  def delete_task(self, task_id: ObjectId):
    collection = self.db["tasks"]
    task = collection.delete_one({"_id": task_id})
    if task.deleted_count == 0:
      raise HTTPException(status_code=404, detail="Task not find")
    return {
      "message": "success"
    }
  def create_dependency(self, task_id: ObjectId, dep_id: ObjectId):
    collection = self.db["tasks"]
    exitsTaskID = collection.find_one({"_id": dep_id})
    if task_id in exitsTaskID.get("dependencies", []):
      raise HTTPException(status_code=400, detail="taskID exit on dep_id")
    exitsDepID = collection.find_one({"_id": task_id})
    if dep_id in exitsDepID.get("dependencies", []):
      raise HTTPException(status_code=400, detail="dep_id exit on taskID")
    result = collection.update_one(
      {"_id": task_id},
      {"$push": {"dependencies":  dep_id}}
    )
    if result.modified_count == 0:
      raise HTTPException(status_code=404, detail="Dependency not found in task")
    return {"message": "success"}
  def delete_dependency(self, task_id: ObjectId, dep_id: ObjectId):
    collection = self.db["tasks"]
    result = collection.update_one(
      {"_id": task_id},
      {"$pull": {"dependencies":  dep_id}}
    )
    if result.modified_count == 0:
      raise HTTPException(status_code=404, detail="Dependency not found in task")
    return {"message": "success"}
  def get_dependency(self, task_id: ObjectId, checkID: dict = {}, datas: list = []):
    if str(task_id) in checkID:
      return 
    task = self.db["tasks"].find_one({"_id": task_id})
    if task:
      checkID[str(task_id)] = True
      task["_id"] = str(task["_id"]) 
      task["dependencies"] = [str(dep) for dep in task.get("dependencies", [])]
      datas.append(task)
      for dep_id in task.get("dependencies", []):
          self.get_dependency(ObjectId(dep_id), checkID=checkID, datas=datas)
      checkID[str(task_id)] = False
  def check_task(self):
    # co the phat trien send mail vao day tai em ban qua nen khong co lam
    collection = self.db["tasks"]
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    upcoming_threshold = now + timedelta(minutes=5)
    upcoming_task = collection.find({
      "completed": False,
      "date": {"$gte": now, "$lte": upcoming_threshold}
    })
    overdue_tasks = collection.find({
      "completed": False,
      "date": {"$lt": now}
    })
    for task in upcoming_task:
      print(f"Nhắc nhở: Nhiệm vụ '{task['title']}' sẽ hết hạn lúc {task['date']}!")
    for task in overdue_tasks:
      print(f"Cảnh báo: Nhiệm vụ '{task['title']}' đã quá hạn vào {task['date']}!")





