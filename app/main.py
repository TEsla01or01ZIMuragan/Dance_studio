from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.auth import ensure_default_admin
from app.routers.auth import router as auth_router
from app.routers.events import router as events_router
from app.routers.schedule import router as schedule_router
from app.routers.trial_requests import router as trial_requests_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Dance Studio API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(schedule_router)
app.include_router(trial_requests_router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


@app.on_event("startup")
async def startup_event() -> None:
    await ensure_default_admin()


@app.get("/")
async def read_home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/about")
async def read_about():
    return FileResponse(BASE_DIR / "about.html")


@app.get("/news")
async def read_news():
    return FileResponse(BASE_DIR / "news.html")


@app.get("/schedule-page")
async def read_schedule_page():
    return FileResponse(BASE_DIR / "schedule.html")


@app.get("/admin")
async def read_admin_page():
    return FileResponse(BASE_DIR / "admin.html")


@app.get("/{file_path:path}")
async def serve_project_file(file_path: str):
    target = (BASE_DIR / file_path).resolve()
    if BASE_DIR not in target.parents and target != BASE_DIR:
        raise HTTPException(status_code=404, detail="File not found")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)
