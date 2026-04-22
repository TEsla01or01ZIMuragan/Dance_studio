from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_collection
from app.dependencies import get_current_admin
from app.schemas import ScheduleCreate, ScheduleOut, ScheduleUpdate

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


WEEKDAY_ORDER = {
    "Понедельник": 1,
    "Вторник": 2,
    "Среда": 3,
    "Четверг": 4,
    "Пятница": 5,
    "Суббота": 6,
    "Воскресенье": 7,
}


def serialize_schedule(doc: dict) -> ScheduleOut:
    return ScheduleOut(
        id=str(doc["_id"]),
        title=doc["title"],
        teacher=doc["teacher"],
        weekday=doc["weekday"],
        start_time=doc["start_time"],
        end_time=doc["end_time"],
        hall=doc.get("hall"),
        level=doc.get("level"),
        created_at=doc["created_at"],
    )


@router.get("", response_model=list[ScheduleOut])
async def list_schedule():
    docs = await get_collection("schedule").find().to_list(length=500)
    docs.sort(key=lambda item: (WEEKDAY_ORDER.get(item.get("weekday", ""), 99), item.get("start_time", "")))
    return [serialize_schedule(doc) for doc in docs]


@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule_item(payload: ScheduleCreate, admin=Depends(get_current_admin)):
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await get_collection("schedule").insert_one(doc)
    created = await get_collection("schedule").find_one({"_id": result.inserted_id})
    return serialize_schedule(created)


@router.put("/{item_id}", response_model=ScheduleOut)
async def update_schedule_item(item_id: str, payload: ScheduleUpdate, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Schedule item not found")

    await get_collection("schedule").update_one({"_id": ObjectId(item_id)}, {"$set": payload.model_dump()})
    updated = await get_collection("schedule").find_one({"_id": ObjectId(item_id)})
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule item not found")
    return serialize_schedule(updated)


@router.delete("/{item_id}")
async def delete_schedule_item(item_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=404, detail="Schedule item not found")

    result = await get_collection("schedule").delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schedule item not found")
    return {"ok": True}
