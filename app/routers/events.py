from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db import get_collection
from app.dependencies import get_current_admin
from app.schemas import EventCreate, EventOut, EventUpdate

router = APIRouter(prefix="/api/events", tags=["events"])


def serialize_event(doc: dict) -> EventOut:
    event_date = doc["event_date"]
    now = datetime.now(timezone.utc)
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)
    return EventOut(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc["description"],
        event_date=event_date,
        image=doc.get("image"),
        location=doc.get("location"),
        created_at=doc["created_at"],
        is_past=event_date < now,
    )


@router.get("", response_model=list[EventOut])
async def list_events(scope: str = Query(default="all", pattern="^(all|upcoming|past)$")):
    docs = await get_collection("events").find().sort("event_date", 1).to_list(length=500)
    items = [serialize_event(doc) for doc in docs]
    if scope == "upcoming":
        return [item for item in items if not item.is_past]
    if scope == "past":
        return [item for item in items if item.is_past]
    return items


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(payload: EventCreate, admin=Depends(get_current_admin)):
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await get_collection("events").insert_one(doc)
    created = await get_collection("events").find_one({"_id": result.inserted_id})
    return serialize_event(created)


@router.put("/{event_id}", response_model=EventOut)
async def update_event(event_id: str, payload: EventUpdate, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=404, detail="Event not found")

    await get_collection("events").update_one({"_id": ObjectId(event_id)}, {"$set": payload.model_dump()})
    updated = await get_collection("events").find_one({"_id": ObjectId(event_id)})
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return serialize_event(updated)


@router.delete("/{event_id}")
async def delete_event(event_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=404, detail="Event not found")

    result = await get_collection("events").delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"ok": True}
