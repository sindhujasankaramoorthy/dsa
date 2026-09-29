import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("freshgrade.database")

# Try importing pymongo
try:
    import pymongo
    from pymongo import MongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False

class MemoryStorage:
    """In-memory + JSON file backup database fallback when MongoDB is unavailable."""
    def __init__(self, data_file="freshgrade_local_db.json"):
        self.data_file = data_file
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "inspections": [],
            "batches": [],
            "produce_types": [
                {"id": "tomato", "name": "Tomato", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🍅"},
                {"id": "potato", "name": "Potato", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🥔"},
                {"id": "bitter_gourd", "name": "Bitter Gourd", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🥒"},
                {"id": "pointed_gourd", "name": "Pointed Gourd", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🥒"},
                {"id": "onion", "name": "Onion", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🧅"},
                {"id": "capsicum", "name": "Capsicum", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🫑"},
                {"id": "brinjal", "name": "Brinjal", "category": "Vegetable", "supported_models": ["vegetable_quality_model"], "icon": "🍆"},
                {"id": "apple", "name": "Apple", "category": "Fruit", "supported_models": ["fruit_quality_grader"], "icon": "🍎"},
                {"id": "banana", "name": "Banana", "category": "Fruit", "supported_models": ["fruit_quality_grader"], "icon": "🍌"},
                {"id": "pomegranate", "name": "Pomegranate", "category": "Fruit", "supported_models": ["fruit_quality_grader"], "icon": "🍎"},
                {"id": "orange", "name": "Orange", "category": "Fruit", "supported_models": ["fruit_quality_grader"], "icon": "🍊"},
                {"id": "mango", "name": "Mango", "category": "Fruit", "supported_models": ["fruit_quality_grader"], "icon": "🥭"},
            ],
            "models": [
                {"id": "fruit_quality_grader", "name": "Fruit MobileNetV2 Grader", "version": "1.0", "target": "Fruit"},
                {"id": "vegetable_quality_model", "name": "VegQual Deep Model", "version": "1.0", "target": "Vegetable"},
            ]
        }
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.collections[k] = v
            except Exception as e:
                logger.warning(f"Failed loading local DB file: {e}")

    def save(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.collections, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed saving local DB file: {e}")

    def insert_one(self, collection_name: str, doc: Dict[str, Any]):
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        self.collections[collection_name].append(doc)
        self.save()
        return doc

    def find(self, collection_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        docs = self.collections.get(collection_name, [])
        if not query:
            return docs
        filtered = []
        for d in docs:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(d)
        return filtered

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = self.find(collection_name, query)
        return res[0] if res else None

class DatabaseManager:
    def __init__(self):
        self.mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.environ.get("MONGODB_DB_NAME", "freshgrade_db")
        self.client = None
        self.db = None
        self.is_connected = False
        self.fallback_db = MemoryStorage()

        self._init_connection()

    def _init_connection(self):
        if HAS_PYMONGO:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                # Quick server check
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.is_connected = True
                logger.info(f"Connected to MongoDB at {self.mongo_uri}")
            except Exception as e:
                logger.info(f"MongoDB not reachable ({e}). Operating in Local High-Performance DB Mode.")
                self.is_connected = False

    def get_collection(self, collection_name: str):
        if self.is_connected and self.db is not None:
            return self.db[collection_name]
        return None

    def insert_inspection(self, record: Dict[str, Any]):
        if self.is_connected and self.db is not None:
            self.db["inspections"].insert_one(record)
        self.fallback_db.insert_one("inspections", record)

    def get_inspections(self, query: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            res = list(self.db["inspections"].find(query or {}, {"_id": 0}).sort("timestamp", -1).limit(limit))
            if res:
                return res
        docs = self.fallback_db.find("inspections", query)
        docs_sorted = sorted(docs, key=lambda x: x.get("timestamp", ""), reverse=True)
        return docs_sorted[:limit]

    def insert_batch(self, record: Dict[str, Any]):
        if self.is_connected and self.db is not None:
            self.db["batches"].insert_one(record)
        self.fallback_db.insert_one("batches", record)

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            res = self.db["batches"].find_one({"batch_id": batch_id}, {"_id": 0})
            if res:
                return res
        return self.fallback_db.find_one("batches", {"batch_id": batch_id})

    def get_batches(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            res = list(self.db["batches"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
            if res:
                return res
        docs = self.fallback_db.find("batches")
        docs_sorted = sorted(docs, key=lambda x: x.get("created_at", ""), reverse=True)
        return docs_sorted[:limit]

    def get_produce_types(self) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            res = list(self.db["produce_types"].find({}, {"_id": 0}))
            if res:
                return res
        return self.fallback_db.find("produce_types")

    def insert_produce_type(self, produce: Dict[str, Any]):
        if self.is_connected and self.db is not None:
            self.db["produce_types"].insert_one(produce)
        self.fallback_db.insert_one("produce_types", produce)

db_manager = DatabaseManager()
