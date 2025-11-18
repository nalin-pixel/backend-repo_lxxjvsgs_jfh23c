import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import GymClass, Booking, Plugin

app = FastAPI(title="Gym Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Gym Booking API is running"}

@app.get("/test")
def test_database():
    """Verify database connection and list collections"""
    status = {"backend": "✅ Running", "database": "❌ Not Available", "collections": []}
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["collections"] = db.list_collection_names()
        else:
            status["database"] = "❌ Not Configured"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:80]}"
    return status

# ---------------------- Gym Classes ----------------------

@app.post("/api/classes", status_code=201)
async def create_class(payload: GymClass):
    class_id = create_document("gymclass", payload)
    return {"id": class_id}

@app.get("/api/classes")
async def list_classes(limit: int = 20):
    docs = get_documents("gymclass", limit=limit)
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d["_id"]) if d.get("_id") else None
    return docs

# ---------------------- Bookings ----------------------

@app.post("/api/bookings", status_code=201)
async def create_booking(payload: Booking):
    # Validate class exists
    cid = payload.class_id
    try:
        obj_id = ObjectId(cid)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid class_id")
    cls = db["gymclass"].find_one({"_id": obj_id})
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Capacity check
    capacity = cls.get("capacity", 0)
    booked = db["booking"].count_documents({"class_id": cid})
    if booked >= capacity:
        raise HTTPException(status_code=409, detail="Class is fully booked")

    booking_id = create_document("booking", payload)
    return {"id": booking_id}

@app.get("/api/bookings")
async def list_bookings(class_id: Optional[str] = None, limit: int = 50):
    filt = {"class_id": class_id} if class_id else {}
    docs = get_documents("booking", filter_dict=filt, limit=limit)
    for d in docs:
        d["_id"] = str(d["_id"]) if d.get("_id") else None
    return docs

# ---------------------- Plugins ----------------------

@app.get("/api/plugins")
async def get_plugins():
    docs = get_documents("plugin")
    for d in docs:
        d["_id"] = str(d["_id"]) if d.get("_id") else None
    return docs

class PluginToggle(BaseModel):
    enabled: bool
    config: dict = {}

@app.post("/api/plugins/{key}")
async def upsert_plugin(key: str, payload: PluginToggle):
    existing = db["plugin"].find_one({"key": key})
    data = {"key": key, "name": key.replace(".", " ").title(), "enabled": payload.enabled, "config": payload.config}
    if existing:
        db["plugin"].update_one({"_id": existing["_id"]}, {"$set": data})
        _id = existing["_id"]
    else:
        _id = db["plugin"].insert_one(data).inserted_id
    return {"id": str(_id)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
