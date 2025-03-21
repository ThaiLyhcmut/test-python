from pymongo import MongoClient  # Thêm dòng này vào!
import os

class Database:
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(Database, cls).__new__(cls)

      mongo_url = os.getenv("MONGO_URL")
      db_name = os.getenv("COLLECTION")

      if not mongo_url or not db_name:
        raise ValueError("MONGO URL OR COLLECTION ERROR")

      
      try:
        cls._instance.client = MongoClient(mongo_url)
        cls._instance.db = cls._instance.client[db_name]

        print("connect database SUCCESS")
      except Exception as e:
        print("connect database ERROR")
        cls._instance.db = None

    return cls._instance

  def get_db(self):
    if self.db is None:
      raise Exception("connect database ERROR")
    return self.db
