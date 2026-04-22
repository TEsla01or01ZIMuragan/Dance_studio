from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_collection
from app.dependencies import get_current_admin
from app.schemas import TrialRequestCreate, TrialRequestOut

router = APIRouter(prefix="/api/trial-requests", tags=["trial-requests"])


def serialize_trial_request(doc: dict) -> TrialRequestOut:
    return TrialRequestOut(
        id=str(doc["_id"]),
        name=doc["name"],
        phone=doc["phone"],
        direction=doc.get("direction"),
        comment=doc.get("comment"),
        source=doc.get("source"),
        created_at=doc["created_at"],
    )


@router.post("", response_model=TrialRequestOut, status_code=status.HTTP_201_CREATED)
async def create_trial_request(payload: TrialRequestCreate):
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await get_collection("trial_requests").insert_one(doc)
    created = await get_collection("trial_requests").find_one({"_id": result.inserted_id})
    return serialize_trial_request(created)


@router.get("", response_model=list[TrialRequestOut])
async def list_trial_requests(admin=Depends(get_current_admin)):
    docs = await get_collection("trial_requests").find().sort("created_at", -1).to_list(length=500)
    return [serialize_trial_request(doc) for doc in docs]


@router.delete("/{request_id}")
async def delete_trial_request(request_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=404, detail="Trial request not found")

    result = await get_collection("trial_requests").delete_one({"_id": ObjectId(request_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trial request not found")
    return {"ok": True}
