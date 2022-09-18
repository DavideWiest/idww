import pymongo
import json
import os
from bson.json_util import dumps
from datetime import datetime
from modules.sys_helper import CLogger

os.environ["con_db_username"] = "admin"
os.environ["con_db_password"] = "yeet1234"

os.environ["backup_con_db_username"] = ""
os.environ["backup_con_db_password"] = ""

HOST = "davidewiest.com"
PORT = "27017"
DB_NAME = "instadata"

BACKUP_HOST = None # "localhost"
BACKUP_PORT = "27017"
BACKUP_DB_NAME = "instadata_backup"

primary_collection = backup_primary_collection = "main"

class MongoManager:
    def __init__(self, user=None, password=None, host=HOST, port=PORT, db_name=DB_NAME, backup_user=None, backup_password=None, backup_host=BACKUP_HOST, backup_port=BACKUP_PORT, backup_db_name=BACKUP_DB_NAME):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.backup_user = backup_user
        self.backup_password = backup_password
        self.backup_host = backup_host
        self.backup_port = backup_port
        self.backup_db_name = backup_db_name
        self.last_connection_time = datetime.now()

        self.cl = CLogger()
        self.connect()
        
    def connect(self):
        self.user = os.environ.get("con_db_username") if self.user == None else self.user
        self.password = os.environ.get("con_db_password") if self.password == None else self.password
        uri = f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[self.db_name]

        self.backup_host = self.backup_host
        
        if self.backup_host == None:
            self.backup_client = None
            self.backup_db = None
        elif self.backup_host == "localhost":
            backup_uri = f"mongodb://{self.backup_host}:{self.backup_port}"
            self.backup_client = pymongo.MongoClient(backup_uri)
            self.backup_db = self.backup_client[self.backup_db_name]
        else:
            self.backup_user = os.environ.get("con_db_username") if self.backup_user == None else self.backup_user
            self.backup_password = os.environ.get("con_db_password") if self.backup_password == None else self.backup_password
            backup_uri = f"mongodb://{self.backup_user}:{self.backup_password}@{self.backup_host}:{self.backup_port}"
            self.backup_client = pymongo.MongoClient(backup_uri)
            self.backup_db = self.backup_client[self.backup_db_name]

        self.pcol = self.db[primary_collection]
        if self.backup_host != None:
            self.bcol = self.backup_db[backup_primary_collection]
        else:
            self.bcol = None

        self.last_connection_time = datetime.now()

    def upsert_user(self, data):
        self.pcol.update_one(filter={"insta_id": data["insta_id"]}, update={"$set": data}, upsert=True)
        if self.backup_host != None:
            self.bcol.update_one(filter={"insta_id": data["insta_id"]}, update={"$set": data}, upsert=True)

    def insert_empthy_user(self, id):
        if list(self.pcol.find({"insta_id": id})) == []:
            self.pcol.insert_one({"insta_id": id})
        if self.backup_host != None:
            if list(self.bcol.find({"insta_id": id})) == []:
                self.bcol.insert_one({"insta_id": id})

    def get_all_unpopulized(self):
        unpop_docs = list(self.pcol.find({"populized": False}, {"_id": False, "insta_id": True, "applicable": True}))
        return [doc["insta_id"] for doc in unpop_docs]

    def export_to_json(self, filename):
        cursor = self.pcol.find({})
        with open(f"{filename}.json", "w") as file:
            json.dump(json.loads(dumps(cursor)), file)

    def is_in_db(self, id):
        return self.pcol.find_one({"insta_id": id}, {"_id": False, "insta_id": True, "date_last_upserted_at": True, "populized": True})
    
    def find(self, filter, returnables):
        result = self.pcol.find_one(filter, returnables)
        return result

    def multifind(self, filter={}, returnables=None):
        if returnables == None:
            result = self.pcol.find(filter)
        else:
            result = self.pcol.find(filter, returnables)
            
        return list(result)
